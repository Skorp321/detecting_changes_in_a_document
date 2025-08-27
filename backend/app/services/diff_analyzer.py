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
            # Работаем с параграфами, но анализируем на уровне предложений
            ref_paragraphs = reference_text.get('paragraphs', [])
            client_paragraphs = client_text.get('paragraphs', [])
            
            logger.info(f"Reference paragraphs: {len(ref_paragraphs)}")
            logger.info(f"Client paragraphs: {len(client_paragraphs)}")
            
            changes = []
            
            # Если нет параграфов, работаем с полным текстом
            if not ref_paragraphs or not client_paragraphs:
                ref_text = reference_text.get('text', '')
                client_text_raw = client_text.get('text', '')
                
                # Разделяем на предложения
                ref_sentences = self._split_into_sentences(ref_text)
                client_sentences = self._split_into_sentences(client_text_raw)
                
                # Сравниваем предложения
                changes.extend(self._compare_sentences(ref_sentences, client_sentences, "Документ"))
                
                return changes
            
            # Анализируем каждый параграф отдельно
            max_paragraphs = max(len(ref_paragraphs), len(client_paragraphs))
            
            for para_idx in range(max_paragraphs):
                ref_para = ref_paragraphs[para_idx] if para_idx < len(ref_paragraphs) else ""
                client_para = client_paragraphs[para_idx] if para_idx < len(client_paragraphs) else ""
                
                # Пропускаем одинаковые параграфы
                ref_para_norm = ' '.join(ref_para.split()) if ref_para else ""
                client_para_norm = ' '.join(client_para.split()) if client_para else ""
                
                if ref_para_norm == client_para_norm:
                    continue
                
                # Разделяем параграфы на предложения
                ref_sentences = self._split_into_sentences(ref_para)
                client_sentences = self._split_into_sentences(client_para)
                
                # Сравниваем предложения внутри параграфа
                para_changes = self._compare_sentences(
                    ref_sentences, 
                    client_sentences, 
                    f"Параграф {para_idx + 1}"
                )
                changes.extend(para_changes)
            
            logger.info(f"Found {len(changes)} sentence-level changes")
            return changes
            
        except Exception as e:
            logger.error(f"Error analyzing differences: {e}")
            return []
    
    def _compare_sentences(self, ref_sentences: List[str], client_sentences: List[str], context: str) -> List[DiffChange]:
        """Сравнивает предложения и возвращает изменения"""
        changes = []
        
        # Используем difflib для сравнения списков предложений
        self.sequence_matcher.set_seqs(ref_sentences, client_sentences)
        opcodes = self.sequence_matcher.get_opcodes()
        
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'equal':
                # Одинаковые предложения - пропускаем
                continue
            elif tag == 'delete':
                # Удаленные предложения
                for i in range(i1, i2):
                    sentence = ref_sentences[i]
                    change = DiffChange(
                        original_text=sentence,
                        modified_text="",
                        change_type="deletion",
                        position=i,
                        text=sentence,
                        context=f"{context}, предложение {i+1}",
                        highlighted_original=f"[-]{sentence}[/-]",
                        highlighted_modified=""
                    )
                    changes.append(change)
            elif tag == 'insert':
                # Добавленные предложения
                for j in range(j1, j2):
                    sentence = client_sentences[j]
                    change = DiffChange(
                        original_text="",
                        modified_text=sentence,
                        change_type="addition",
                        position=j,
                        text=sentence,
                        context=f"{context}, предложение {j+1}",
                        highlighted_original="",
                        highlighted_modified=f"[+]{sentence}[/+]"
                    )
                    changes.append(change)
            elif tag == 'replace':
                # Замененные предложения
                # Берем более длинный диапазон для сравнения
                max_range = max(i2 - i1, j2 - j1)
                
                for idx in range(max_range):
                    ref_sentence = ref_sentences[i1 + idx] if (i1 + idx) < i2 else ""
                    client_sentence = client_sentences[j1 + idx] if (j1 + idx) < j2 else ""
                    
                    if ref_sentence == client_sentence:
                        continue
                    
                    if ref_sentence and client_sentence:
                        # Модификация предложения
                        highlighted_orig, highlighted_mod = self._highlight_differences(ref_sentence, client_sentence)
                        
                        change = DiffChange(
                            original_text=ref_sentence,
                            modified_text=client_sentence,
                            change_type="modification",
                            position=i1 + idx,
                            text=client_sentence,
                            context=f"{context}, предложение {i1 + idx + 1}",
                            highlighted_original=highlighted_orig,
                            highlighted_modified=highlighted_mod
                        )
                        changes.append(change)
                    elif ref_sentence:
                        # Удаление
                        change = DiffChange(
                            original_text=ref_sentence,
                            modified_text="",
                            change_type="deletion",
                            position=i1 + idx,
                            text=ref_sentence,
                            context=f"{context}, предложение {i1 + idx + 1}",
                            highlighted_original=f"[-]{ref_sentence}[/-]",
                            highlighted_modified=""
                        )
                        changes.append(change)
                    elif client_sentence:
                        # Добавление
                        change = DiffChange(
                            original_text="",
                            modified_text=client_sentence,
                            change_type="addition",
                            position=j1 + idx,
                            text=client_sentence,
                            context=f"{context}, предложение {j1 + idx + 1}",
                            highlighted_original="",
                            highlighted_modified=f"[+]{client_sentence}[/+]"
                        )
                        changes.append(change)
        
        return changes 