import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import os
import re
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Конфигурация страницы
st.set_page_config(
    page_title="Анализ документов",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Настройки API
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def create_highlighted_html(text, is_original=True, highlighted_text=None):
    """Создает HTML с подсветкой изменений"""
    if not text or text == "N/A":
        return f'<div style="color: {"#d32f2f" if is_original else "#2e7d32"}; font-weight: bold; font-style: italic;">Пусто</div>'

    # Если есть подсветка из backend, используем её
    if highlighted_text:
        # Конвертируем формат подсветки из backend в HTML
        # [-]текст[/-] -> красная подсветка для удаленного
        # [+]текст[/+] -> зеленая подсветка для добавленного
        html_text = highlighted_text
        html_text = re.sub(
            r"\[-\](.*?)\[/-\]",
            r'<span style="background-color: #ffcdd2; color: #d32f2f; font-weight: bold;">\1</span>',
            html_text,
        )
        html_text = re.sub(
            r"\[\+\](.*?)\[/\+\]",
            r'<span style="background-color: #c8e6c9; color: #2e7d32; font-weight: bold;">\1</span>',
            html_text,
        )
        html_text = html_text.replace("\n", "<br>")
    else:
        # Fallback: простая подсветка чисел
        html_text = text.replace("\n", "<br>")
        if is_original:
            html_text = re.sub(
                r"(\d+)",
                r'<span style="background-color: #ffcdd2; color: #d32f2f; font-weight: bold;">\1</span>',
                html_text,
            )
        else:
            html_text = re.sub(
                r"(\d+)",
                r'<span style="background-color: #c8e6c9; color: #2e7d32; font-weight: bold;">\1</span>',
                html_text,
            )

    # Создаем контейнер с соответствующей границей
    if is_original:
        return f'<div style="border-left: 4px solid #d32f2f; padding: 10px; margin: 5px 0; border-radius: 4px; font-size: 14px; line-height: 1.4;">{html_text}</div>'
    else:
        return f'<div style="border-left: 4px solid #2e7d32; padding: 10px; margin: 5px 0; border-radius: 4px; font-size: 14px; line-height: 1.4;">{html_text}</div>'


def highlight_changes(original_text, modified_text):
    """Подсветка изменений в тексте с помощью HTML"""
    # Эта функция теперь использует create_highlighted_html, которая определена выше
    pass


def create_comparison_html(
    original_text, modified_text, highlighted_original=None, highlighted_modified=None
):
    """Создает HTML для сравнения двух текстов с подсветкой"""

    original_html = create_highlighted_html(
        original_text, is_original=True, highlighted_text=highlighted_original
    )
    modified_html = create_highlighted_html(
        modified_text, is_original=False, highlighted_text=highlighted_modified
    )

    comparison_html = f"""
    <div style="display: flex; gap: 20px; margin: 10px 0;">
        <div style="flex: 1;">
            <h4 style="color: #d32f2f; margin-bottom: 10px;">📄 Редакция СБЛ:</h4>
            {original_html}
        </div>
        <div style="flex: 1;">
            <h4 style="color: #2e7d32; margin-bottom: 10px;">📝 Редакция лизингополучателя:</h4>
            {modified_html}
        </div>
    </div>
    """

    return comparison_html


def upload_documents():
    """Вкладка для загрузки документов"""
    st.header("📄 Загрузка документов")
    st.markdown("Загрузите два документа для сравнения и анализа")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📋 Экземпляр компании")
        company_doc = st.file_uploader(
            "Выберите документ компании", type=["pdf", "docx", "txt"], key="company_doc"
        )

        if company_doc:
            st.success(f"✅ Загружен: {company_doc.name}")
            st.info(f"Размер: {company_doc.size / 1024:.1f} KB")

    with col2:
        st.subheader("👤 Экземпляр клиента")
        client_doc = st.file_uploader(
            "Выберите документ клиента", type=["pdf", "docx", "txt"], key="client_doc"
        )

        if client_doc:
            st.success(f"✅ Загружен: {client_doc.name}")
            st.info(f"Размер: {client_doc.size / 1024:.1f} KB")

    # Кнопка запуска анализа
    if company_doc and client_doc:
        if st.button("🚀 Запустить анализ", type="primary", use_container_width=True):
            with st.spinner("Выполняется анализ документов..."):
                try:
                    # Подготавливаем файлы для отправки
                    files = {
                        "reference_doc": (
                            company_doc.name,
                            company_doc.getvalue(),
                            company_doc.type,
                        ),
                        "client_doc": (
                            client_doc.name,
                            client_doc.getvalue(),
                            client_doc.type,
                        ),
                    }

                    # Отправляем запрос на API
                    response = requests.post(
                        f"{API_BASE_URL}/api/compare",
                        files=files,
                        timeout=300,  # 5 минут таймаут
                    )

                    if response.status_code == 200:
                        result = response.json()
                        # Сохраняем результат в session state
                        st.session_state.analysis_result = result
                        st.session_state.analysis_completed = True
                        st.success("✅ Анализ завершен успешно!")
                        st.rerun()
                    else:
                        st.error(f"❌ Ошибка при анализе: {response.text}")

                except requests.exceptions.Timeout:
                    st.error("⏰ Превышено время ожидания. Попробуйте снова.")
                except requests.exceptions.ConnectionError:
                    st.error(
                        "🔌 Ошибка подключения к серверу. Проверьте, что API сервер запущен."
                    )
                except Exception as e:
                    st.error(f"❌ Неожиданная ошибка: {str(e)}")
    else:
        st.warning("⚠️ Загрузите оба документа для начала анализа")


def display_results():
    """Вкладка для отображения результатов"""
    st.header("📊 Результаты анализа")

    if not st.session_state.get("analysis_completed", False):
        st.info(
            "ℹ️ Сначала выполните анализ документов на вкладке 'Загрузка документов'"
        )
        return

    result = st.session_state.get("analysis_result")
    if not result:
        st.error("❌ Результаты анализа не найдены")
        return

    # Отображение сводки
    st.subheader("📋 Сводка анализа")
    summary = result.get("summary", {})

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Всего изменений", summary.get("totalChanges", 0))

    with col2:
        st.metric("Критических изменений", summary.get("criticalChanges", 0))

    with col3:
        st.metric("Время обработки", summary.get("processingTime", "N/A"))

    with col4:
        st.metric("ID анализа", result.get("analysisId", "N/A")[:8] + "...")

    # Информация о документах
    st.subheader("📄 Анализируемые документы")
    doc_info = summary.get("documentPair", {})
    col1, col2 = st.columns(2)

    with col1:
        st.info(f"**Документ компании:** {doc_info.get('referenceDoc', 'N/A')}")

    with col2:
        st.info(f"**Документ клиента:** {doc_info.get('clientDoc', 'N/A')}")

    # Детальный анализ изменений
    st.subheader("� Детальный анализ изменений")

    changes = result.get("changes", [])
    if not changes:
        st.info("ℹ️ Изменения не обнаружены")
        return

    # Создаем DataFrame для отображения в формате таблицы сравнения
    df_data = []
    for change in changes:
        # Используем данные подсветки из backend
        original_text = change.get("originalText", "N/A")
        modified_text = change.get("modifiedText", "N/A")
        highlighted_original = change.get("highlightedOriginal", original_text)
        highlighted_modified = change.get("highlightedModified", modified_text)

        # Конвертируем подсветку в markdown формат для таблицы
        # [-]текст[/-] -> **текст** (жирный для удаленного)
        # [+]текст[/+] -> **текст** (жирный для добавленного)
        original_markdown = re.sub(r"\[-\](.*?)\[/-\]", r"**\1**", highlighted_original)
        original_markdown = re.sub(r"\[\+\](.*?)\[/\+\]", r"**\1**", original_markdown)

        modified_markdown = re.sub(r"\[-\](.*?)\[/-\]", r"**\1**", highlighted_modified)
        modified_markdown = re.sub(r"\[\+\](.*?)\[/\+\]", r"**\1**", modified_markdown)

        # Создаем HTML для служб с отметками от нейросети
        services = change.get("requiredServices", [])
        if services:
            services_text = ", ".join([f"{service}" for service in services])
        else:
            services_text = "⚠️ Не указаны"

        df_data.append(
            {
                "Редакция СБЛ": original_markdown,
                "Редакция лизингополучателя": modified_markdown,
                "Комментарии LLM": change.get("llmComment", "N/A"),
                "Необходимые согласования": services_text,
            }
        )

    df = pd.DataFrame(df_data)

    # Отображаем таблицу сравнения
    st.markdown("### 📋 Таблица сравнения документов")

    # Настройки отображения таблицы
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "Редакция СБЛ": st.column_config.TextColumn(
                "Редакция СБЛ",
                width="medium",
                help="Исходный текст из документа компании",
            ),
            "Редакция лизингополучателя": st.column_config.TextColumn(
                "Редакция лизингополучателя",
                width="medium",
                help="Измененный текст из документа клиента",
            ),
            "Комментарии LLM": st.column_config.TextColumn(
                "Комментарии LLM",
                width="large",
                help="Анализ изменений от искусственного интеллекта",
            ),
            "Необходимые согласования": st.column_config.TextColumn(
                "Необходимые согласования",
                width="medium",
                help="Службы, которые должны согласовать изменения",
            ),
        },
        hide_index=True,
    )

    # Детальный просмотр изменений
    st.subheader("🔬 Детальный анализ изменений")

    for i, change in enumerate(changes):
        with st.expander(
            f"Изменение {i+1}: {change.get('changeType', 'N/A')} - {change.get('severity', 'N/A')}"
        ):

            # Подсветка изменений с помощью HTML
            original_text = change.get("originalText", "N/A")
            modified_text = change.get("modifiedText", "N/A")
            highlighted_original = change.get("highlightedOriginal", None)
            highlighted_modified = change.get("highlightedModified", None)

            comparison_html = create_comparison_html(
                original_text, modified_text, highlighted_original, highlighted_modified
            )
            st.markdown(comparison_html, unsafe_allow_html=True)

            # Анализ ИИ
            st.markdown("**🤖 Анализ Ассистента:**")
            st.info(change.get("llmComment", "N/A"))

            # Метаданные и службы согласования
            col3, col4 = st.columns(2)

            with col3:
                st.markdown("**🏢 Службы согласования:**")

                # Стандартные службы с описаниями
                standard_services = [
                    "ЮрУ",
                    "ДСКБ", 
                    "ПА",
                    "ФС",
                    "УСДС",
                    "РД/УБУ",
                    "КД",
                ]
                
                service_descriptions = {
                    "ЮрУ": "Юридическое управление",
                    "ДСКБ": "Департамент скоринга и кредитного бизнеса",
                    "ПА": "Правовой анализ",
                    "ФС": "Финансовая служба",
                    "УСДС": "Управление стратегического развития и стандартизации",
                    "РД/УБУ": "Риск-департамент/Управление бизнес-услуг",
                    "КД": "Кредитный департамент"
                }
                
                current_services = change.get("requiredServices", [])

                # Создаем чекбоксы для каждой службы с автоматической отметкой
                selected_change_services = []
                
                for service in standard_services:
                    is_selected = service in current_services
                    description = service_descriptions.get(service, service)
                    
                    # Создаем уникальный ключ для каждого чекбокса
                    checkbox_key = f"change_{i}_{service}_{change.get('id', i)}"
                    
                    if st.checkbox(
                        f"{service} - {description}",
                        value=is_selected,
                        key=checkbox_key,
                        help=f"Автоматически отмечено нейросетью: {'Да' if is_selected else 'Нет'}"
                    ):
                        selected_change_services.append(service)
                
                # Показываем статус автоматического выбора
                if current_services:
                    st.success(f"✅ Ассистент рекомендует {len(current_services)} служб для согласования")
                    st.markdown(f"**Автоматически выбрано:** {', '.join(current_services)}")
                else:
                    st.warning("⚠️ Ассистент не определил необходимые службы")

            with col4:
                st.markdown("**📊 Метаданные:**")
                st.markdown(f"• **Тип изменения:** {change.get('changeType', 'N/A')}")
                st.markdown(f"• **Серьезность:** {change.get('severity', 'N/A')}")
                st.markdown(f"• **Уверенность:** {(change.get('confidence', 0) * 100):.1f}%")
                st.markdown(f"• **Дата:** {change.get('createdAt', 'N/A')}")

                # Показываем выбранные службы для этого изменения
                if selected_change_services:
                    st.markdown(f"**Выбрано:** {', '.join(selected_change_services)}")
                
                # Уровень уверенности нейросети в выборе служб
                service_confidence = change.get("serviceConfidence", 0)
                if service_confidence > 0:
                    st.markdown(f"**🎯 Уверенность ассистента в выборе служб:** {service_confidence:.1f}%")
                    
                    # Прогресс-бар для уверенности
                    st.progress(service_confidence / 100)
                    
                    if service_confidence < 50:
                        st.warning("⚠️ Низкая уверенность - рекомендуется ручная проверка")
                    elif service_confidence < 80:
                        st.info("ℹ️ Средняя уверенность - рекомендуется дополнительная проверка")
                    else:
                        st.success("✅ Высокая уверенность в выборе служб")

            # Разделитель между изменениями
            st.markdown("---")


def main():
    """Главная функция приложения"""
    st.title("🔍 Система анализа документов")
    st.markdown("---")

    # Создаем вкладки
    tab1, tab2 = st.tabs(["📄 Загрузка документов", "📊 Результаты анализа"])

    with tab1:
        upload_documents()

    with tab2:
        display_results()

    # Боковая панель с информацией
    with st.sidebar:
        st.header("ℹ️ Информация")
        st.markdown(
            """
        **Поддерживаемые форматы:**
        - PDF (.pdf)
        - Word (.docx)
        - Текст (.txt)
        
        **Максимальный размер файла:** 10 MB
        
        **Статус API:** 
        """
        )

        # Проверка статуса API
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ API доступен")
            else:
                st.error("❌ API недоступен")
        except:
            st.error("❌ API недоступен")

        st.markdown("---")

        if st.button("🔄 Очистить результаты", use_container_width=True):
            if "analysis_result" in st.session_state:
                del st.session_state.analysis_result
            if "analysis_completed" in st.session_state:
                del st.session_state.analysis_completed
            st.rerun()


if __name__ == "__main__":
    main()
