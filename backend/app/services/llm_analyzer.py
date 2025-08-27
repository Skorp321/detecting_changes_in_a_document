import logging
import asyncio
from typing import List, Dict, Any
from dataclasses import dataclass
from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class LLMAnalysisResult:
    """Result of LLM analysis"""
    comment: str
    required_services: List[str]
    severity: str
    confidence: float
    reasoning: str = ""


class LLMAnalyzer:
    """Service for LLM-powered analysis of document changes"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        self.model = settings.OPENAI_MODEL
    
    async def analyze_change(self, change, regulations: List[Dict]) -> LLMAnalysisResult:
        """
        Analyze a specific change using LLM
        
        Args:
            change: The change object containing original and modified text
            regulations: List of relevant regulations
            
        Returns:
            LLMAnalysisResult: Analysis result
        """
        try:
            # Create context from regulations
            regulations_context = self._create_regulations_context(regulations)
            
            # Create prompt for LLM
            prompt = self._create_analysis_prompt(change, regulations_context)
            
            # Make request to OpenAI API using the library
            response = await self._make_api_request(prompt)
            
            # Parse response
            content = response.choices[0].message.content
            return self._parse_llm_response(content)
            
        except Exception as e:
            logger.error(f"Error in LLM analysis: {str(e)}")
            # Return fallback analysis
            return LLMAnalysisResult(
                comment=f"Невозможно проанализировать изменение: {str(e)}",
                required_services=["Общий анализ"],
                severity="medium",
                confidence=0.1,
                reasoning="Ошибка при обращении к LLM"
            )
    
    async def _make_api_request(self, prompt: str):
        """Make request to OpenAI API using the library"""
        def sync_request():
            return self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS,
            )
        
        # Run synchronous OpenAI client in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, sync_request)
    
    def _create_regulations_context(self, regulations: List[Dict]) -> str:
        """Create context string from regulations"""
        if not regulations:
            return "Нет доступных нормативных документов для анализа."
        
        context = "Релевантные нормативные документы:\n"
        for reg in regulations:
            context += f"- {reg.get('title', 'Без названия')}: {reg.get('content', '')[:200]}...\n"
        
        return context
    
    def _create_analysis_prompt(self, change, regulations_context: str) -> str:
        """Create analysis prompt for LLM"""
        original_text = getattr(change, 'original_text', '')
        modified_text = getattr(change, 'modified_text', '')
        
        prompt = f"""
            Проанализируйте изменение в документе и определите необходимые согласования.

            ИСХОДНЫЙ ТЕКСТ:
            {original_text}

            РЕДАКЦИЯ ЛИЗИНГОПОЛУЧАТЕЛЯ:
            {modified_text}

            НОРМАТИВНАЯ БАЗА:
            {regulations_context}

            Пожалуйста, предоставьте анализ в следующем формате:
            КОММЕНТАРИЙ: [Краткое описание изменения и его последствий]
            СОГЛАСОВАНИЯ: [Список необходимых служб через запятую, надо выбрать из списка: 
                    ЮрУ - юридическое управление,
                    ДСКБ - Департамент сопровождения клиентов и бизнеса,
                    ПА - проблемные активы,
                    ФС - финансовая служба,
                    УСДС - управление страхования,
                    РД/УБУ - управление бухгалтерского учета,
                    КД - кредитный департамент.
                    В ответе должны быть только названия служб, без пробелов и других символов и без описания]
            КРИТИЧНОСТЬ: [low/medium/high]
            УВЕРЕННОСТЬ: [число от 0 до 1]
            ОБОСНОВАНИЕ: [Подробное объяснение решения. Объясни что и почему нужно проверить]
            """
        return prompt
    
    def _parse_llm_response(self, content: str) -> LLMAnalysisResult:
        """Parse LLM response and extract structured data"""
        try:
            # Default values
            comment = "Изменение требует проверки"
            required_services = ["Общий анализ"]
            severity = "medium"
            confidence = 0.5
            reasoning = "Стандартный анализ"
            
            # Simple parsing logic
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('КОММЕНТАРИЙ:'):
                    comment = line.replace('КОММЕНТАРИЙ:', '').strip()
                elif line.startswith('СОГЛАСОВАНИЯ:'):
                    services_str = line.replace('СОГЛАСОВАНИЯ:', '').strip()
                    required_services = [s.strip() for s in services_str.split(',') if s.strip()]
                elif line.startswith('КРИТИЧНОСТЬ:'):
                    severity = line.replace('КРИТИЧНОСТЬ:', '').strip().lower()
                    # Remove square brackets if present
                    severity = severity.strip('[]')
                    # Validate severity value
                    if severity not in ['low', 'medium', 'high', 'critical']:
                        severity = 'medium'  # default fallback
                elif line.startswith('УВЕРЕННОСТЬ:'):
                    try:
                        confidence = float(line.replace('УВЕРЕННОСТЬ:', '').strip())
                    except ValueError:
                        confidence = 0.5
                elif line.startswith('ОБОСНОВАНИЕ:'):
                    reasoning = line.replace('ОБОСНОВАНИЕ:', '').strip()
            
            return LLMAnalysisResult(
                comment=comment,
                required_services=required_services,
                severity=severity,
                confidence=confidence,
                reasoning=reasoning
            )
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            return LLMAnalysisResult(
                comment="Ошибка при разборе ответа LLM",
                required_services=["Общий анализ"],
                severity="medium",
                confidence=0.1,
                reasoning=f"Ошибка парсинга: {str(e)}"
            )
    
    async def mock_analyze_change(self, change, regulations: List[Dict]) -> LLMAnalysisResult:
        """Mock analysis for testing without API key"""
        return LLMAnalysisResult(
            comment="Обнаружено изменение в тексте документа",
            required_services=["Юридический отдел", "Отдел качества"],
            severity="medium",
            confidence=0.8,
            reasoning="Мок-анализ для тестирования"
        ) 