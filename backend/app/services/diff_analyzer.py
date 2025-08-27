import difflib
import logging
import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DiffChange:
    """Represents a change between two documents"""
    original_text: str
    modified_text: str
    change_type: str
    position: int
    text: str
    context: str = ""
    highlighted_original: str = ""  # Редакция СБЛ с подсветкой
    highlighted_modified: str = ""  # Редакция лизингополучателя с подсветкой
    

class DiffAnalyzer:
    """Service for analyzing differences between documents"""
    
    def __init__(self):
        self.sequence_matcher = difflib.SequenceMatcher()
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Разделяет текст на предложения"""
        if not text:
            return []
        
        # Разделяем по точкам, восклицательным и вопросительным знакам
        sentences = re.split(r'[.!?]+', text)
        
        # Убираем пустые предложения и очищаем пробелы
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def _split_into_subparagraphs(self, text: str) -> List[Dict[str, Any]]:
        """
        Разделяет текст на подпункты (от цифры с номером подпункта до следующей цифры)
        Возвращает список словарей с информацией о подпунктах
        """
        if not text:
            return []
        
        # Паттерн для поиска подпунктов: цифра с точкой или скобкой в начале строки
        # Поддерживаем различные форматы: 1., 1), 1.1., 1.1), и т.д.
        # Также поддерживаем римские цифры и буквы: I., II., a), б), и т.д.
        subparagraph_pattern = r'^([0-9]+(?:\.\d+)*[\.\)]|[IVX]+[\.\)]|[а-яё][\.\)]|[a-z][\.\)])\s*(.*?)(?=\n\s*([0-9]+(?:\.\d+)*[\.\)]|[IVX]+[\.\)]|[а-яё][\.\)]|[a-z][\.\)])|\Z)'
        
        # Ищем все подпункты в тексте
        matches = list(re.finditer(subparagraph_pattern, text, re.MULTILINE | re.DOTALL))
        
        subparagraphs = []
        
        if matches:
            for i, match in enumerate(matches):
                number = match.group(1)
                content = match.group(2).strip()
                
                # Определяем границы подпункта
                start_pos = match.start()
                if i < len(matches) - 1:
                    end_pos = matches[i + 1].start()
                else:
                    end_pos = len(text)
                
                full_subparagraph = text[start_pos:end_pos].strip()
                
                subparagraphs.append({
                    'number': number,
                    'content': content,
                    'full_text': full_subparagraph,
                    'start_pos': start_pos,
                    'end_pos': end_pos
                })
        else:
            # Если подпункты не найдены, разбиваем на предложения
            sentences = self._split_into_sentences(text)
            for i, sentence in enumerate(sentences):
                subparagraphs.append({
                    'number': f"{i+1}.",
                    'content': sentence,
                    'full_text': sentence,
                    'start_pos': 0,
                    'end_pos': len(sentence)
                })
        
        return subparagraphs
    
    def _find_subparagraph_for_position(self, subparagraphs: List[Dict[str, Any]], position: int) -> Dict[str, Any]:
        """
        Находит подпункт, в котором находится указанная позиция
        """
        for subpara in subparagraphs:
            if subpara['start_pos'] <= position < subpara['end_pos']:
                return subpara
        
        # Если не найден, ищем ближайший подпункт
        if subparagraphs:
            # Находим подпункт с наименьшим расстоянием до позиции
            closest_subpara = min(subparagraphs, key=lambda x: abs(x['start_pos'] - position))
            return closest_subpara
        
        # Если подпунктов нет, возвращаем пустой
        return {'number': '1.', 'content': '', 'full_text': ''}
    
    def _highlight_differences(self, text1: str, text2: str) -> Tuple[str, str]:
        """Подсвечивает различия между двумя текстами"""
        if not text1 and not text2:
            return "", ""
        if not text1:
            return "", f"[+]{text2}[/+]"
        if not text2:
            return f"[-]{text1}[/-]", ""
        
        # Используем difflib для поиска различий на уровне слов
        words1 = text1.split()
        words2 = text2.split()
        
        self.sequence_matcher.set_seqs(words1, words2)
        opcodes = self.sequence_matcher.get_opcodes()
        
        highlighted1 = []
        highlighted2 = []
        
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'equal':
                # Одинаковые части
                equal_words1 = words1[i1:i2]
                equal_words2 = words2[j1:j2]
                highlighted1.extend(equal_words1)
                highlighted2.extend(equal_words2)
            elif tag == 'delete':
                # Удаленные слова
                deleted_words = words1[i1:i2]
                highlighted1.extend([f"[-]{word}[/-]" for word in deleted_words])
            elif tag == 'insert':
                # Добавленные слова
                inserted_words = words2[j1:j2]
                highlighted2.extend([f"[+]{word}[/+]" for word in inserted_words])
            elif tag == 'replace':
                # Замененные слова
                old_words = words1[i1:i2]
                new_words = words2[j1:j2]
                highlighted1.extend([f"[-]{word}[/-]" for word in old_words])
                highlighted2.extend([f"[+]{word}[/+]" for word in new_words])
        
        return ' '.join(highlighted1), ' '.join(highlighted2)
    
    async def analyze_differences(self, reference_text: Dict, client_text: Dict) -> List[DiffChange]:
        """Analyze differences between two document texts"""
        try:
            # Всегда работаем с полным текстом и разбиваем его на подпункты
            ref_text = reference_text.get('text', '')
            client_text_raw = client_text.get('text', '')
            
            logger.info(f"Reference text length: {len(ref_text)}")
            logger.info(f"Client text length: {len(client_text_raw)}")
            
            # Разделяем на подпункты
            ref_subparagraphs = self._split_into_subparagraphs(ref_text)
            client_subparagraphs = self._split_into_subparagraphs(client_text_raw)
            
            logger.info(f"Reference subparagraphs: {len(ref_subparagraphs)}")
            logger.info(f"Client subparagraphs: {len(client_subparagraphs)}")
            
            # Сравниваем подпункты целиком
            changes = self._compare_subparagraphs(
                ref_subparagraphs, client_subparagraphs, "Документ"
            )
            
            logger.info(f"Found {len(changes)} subparagraph-level changes")
            return changes
            
        except Exception as e:
            logger.error(f"Error analyzing differences: {e}")
            return []
    
    def _compare_subparagraphs(self, ref_subparagraphs: List[Dict[str, Any]], 
                              client_subparagraphs: List[Dict[str, Any]], 
                              context: str) -> List[DiffChange]:
        """Сравнивает подпункты целиком и возвращает изменения"""
        changes = []
        
        # Создаем списки текстов подпунктов для сравнения
        ref_texts = [subpara['full_text'] for subpara in ref_subparagraphs]
        client_texts = [subpara['full_text'] for subpara in client_subparagraphs]
        
        # Используем difflib для сравнения списков подпунктов
        self.sequence_matcher.set_seqs(ref_texts, client_texts)
        opcodes = self.sequence_matcher.get_opcodes()
        
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'equal':
                # Одинаковые подпункты - пропускаем
                continue
            elif tag == 'delete':
                # Удаленные подпункты
                for i in range(i1, i2):
                    subpara = ref_subparagraphs[i]
                    
                    change = DiffChange(
                        original_text=subpara['full_text'],  # Полный текст подпункта с номером
                        modified_text="",
                        change_type="deletion",
                        position=i,
                        text=subpara['full_text'],
                        context=f"{context}, подпункт {subpara['number']}",
                        highlighted_original=f"[-]{subpara['full_text']}[/-]",
                        highlighted_modified=""
                    )
                    changes.append(change)
            elif tag == 'insert':
                # Добавленные подпункты
                for j in range(j1, j2):
                    subpara = client_subparagraphs[j]
                    
                    change = DiffChange(
                        original_text="",
                        modified_text=subpara['full_text'],  # Полный текст подпункта с номером
                        change_type="addition",
                        position=j,
                        text=subpara['full_text'],
                        context=f"{context}, подпункт {subpara['number']}",
                        highlighted_original="",
                        highlighted_modified=f"[+]{subpara['full_text']}[/+]"
                    )
                    changes.append(change)
            elif tag == 'replace':
                # Замененные подпункты
                # Берем более длинный диапазон для сравнения
                max_range = max(i2 - i1, j2 - j1)
                
                for idx in range(max_range):
                    ref_subpara = ref_subparagraphs[i1 + idx] if (i1 + idx) < i2 else None
                    client_subpara = client_subparagraphs[j1 + idx] if (j1 + idx) < j2 else None
                    
                    if ref_subpara and client_subpara:
                        # Модификация подпункта
                        highlighted_orig, highlighted_mod = self._highlight_differences(
                            ref_subpara['full_text'], client_subpara['full_text']  # Полный текст с номером
                        )
                        
                        change = DiffChange(
                            original_text=ref_subpara['full_text'],  # Полный текст подпункта с номером
                            modified_text=client_subpara['full_text'],
                            change_type="modification",
                            position=i1 + idx,
                            text=client_subpara['full_text'],
                            context=f"{context}, подпункт {ref_subpara['number']}",
                            highlighted_original=highlighted_orig,
                            highlighted_modified=highlighted_mod
                        )
                        changes.append(change)
                    elif ref_subpara:
                        # Удаление подпункта
                        change = DiffChange(
                            original_text=ref_subpara['full_text'],  # Полный текст подпункта с номером
                            modified_text="",
                            change_type="deletion",
                            position=i1 + idx,
                            text=ref_subpara['full_text'],
                            context=f"{context}, подпункт {ref_subpara['number']}",
                            highlighted_original=f"[-]{ref_subpara['full_text']}[/-]",
                            highlighted_modified=""
                        )
                        changes.append(change)
                    elif client_subpara:
                        # Добавление подпункта
                        change = DiffChange(
                            original_text="",
                            modified_text=client_subpara['full_text'],  # Полный текст подпункта с номером
                            change_type="addition",
                            position=j1 + idx,
                            text=client_subpara['full_text'],
                            context=f"{context}, подпункт {client_subpara['number']}",
                            highlighted_original="",
                            highlighted_modified=f"[+]{client_subpara['full_text']}[/+]"
                        )
                        changes.append(change)
        
        return changes 