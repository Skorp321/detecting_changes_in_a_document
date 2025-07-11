import logging
import openai
from typing import List, Dict, Any
from dataclasses import dataclass

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
        openai.api_key = settings.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def analyze_change(self, change, regulations: List[Dict]) -> LLMAnalysisResult:
        """Analyze a document change using LLM"""
        try:
            # For development, return a mock result
            if settings.OPENAI_API_KEY == "sk-dummy-key-for-development":
                return self._mock_analysis(change)
            
            # Real LLM analysis would go here
            prompt = self._create_analysis_prompt(change, regulations)
            
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Вы эксперт по анализу изменений в документах и нормативному соответствию."},
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS
            )
            
            return self._parse_llm_response(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error in LLM analysis: {e}")
            return self._mock_analysis(change)
    
    def _mock_analysis(self, change) -> LLMAnalysisResult:
        """Mock analysis for development"""
        severity_map = {
            "addition": "medium",
            "deletion": "high", 
            "modification": "medium"
        }
        
        return LLMAnalysisResult(
            comment=f"Обнаружено изменение типа '{change.change_type}'. Требуется проверка соответствия нормативным требованиям.",
            required_services=["Юридическая служба", "Служба комплаенс"],
            severity=severity_map.get(change.change_type, "medium"),
            confidence=0.85,
            reasoning="Автоматический анализ на основе типа изменения"
        )
    
    def _create_analysis_prompt(self, change, regulations: List[Dict]) -> str:
        """Create prompt for LLM analysis"""
        prompt = f"""
        Проанализируйте следующее изменение в документе:
        
        Оригинальный текст: {change.original_text}
        Измененный текст: {change.modified_text}
        Тип изменения: {change.change_type}
        
        Релевантные нормативные документы:
        """
        
        for reg in regulations[:3]:  # Limit to top 3
            prompt += f"\n- {reg['title']}: {reg['content'][:100]}..."
        
        prompt += """
        
        Пожалуйста, предоставьте:
        1. Комментарий об изменении (2-3 предложения)
        2. Список необходимых служб для согласования
        3. Уровень критичности (low, medium, high, critical)
        4. Уровень уверенности (0.0-1.0)
        5. Обоснование решения
        
        Формат ответа:
        КОММЕНТАРИЙ: [ваш комментарий]
        СЛУЖБЫ: [служба1, служба2, ...]
        КРИТИЧНОСТЬ: [уровень]
        УВЕРЕННОСТЬ: [число]
        ОБОСНОВАНИЕ: [обоснование]
        """
        
        return prompt
    
    def _parse_llm_response(self, response: str) -> LLMAnalysisResult:
        """Parse LLM response into structured result"""
        try:
            lines = response.strip().split('\n')
            result = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    result[key.strip().upper()] = value.strip()
            
            services = []
            if 'СЛУЖБЫ' in result:
                services = [s.strip() for s in result['СЛУЖБЫ'].split(',')]
            
            confidence = 0.5
            if 'УВЕРЕННОСТЬ' in result:
                try:
                    confidence = float(result['УВЕРЕННОСТЬ'])
                except:
                    confidence = 0.5
            
            return LLMAnalysisResult(
                comment=result.get('КОММЕНТАРИЙ', 'Анализ выполнен'),
                required_services=services,
                severity=result.get('КРИТИЧНОСТЬ', 'medium').lower(),
                confidence=confidence,
                reasoning=result.get('ОБОСНОВАНИЕ', '')
            )
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return LLMAnalysisResult(
                comment="Ошибка анализа LLM",
                required_services=["Юридическая служба"],
                severity="medium",
                confidence=0.3
            ) 