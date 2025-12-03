import csv
from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
import streamlit as st

# Встановлення стилю для графіків (використовуємо універсальний стиль)
plt.style.use('ggplot')

# 1. ООП: СУТНОСТІ ШКОЛИ
#Абстрактний базовий клас(Абстракція)
class Person(ABC):
    def __init__(self, last_name: str, first_name: str, middle_name: str):
        self.last_name: str = last_name
        self.first_name: str = first_name
        self.middle_name: str = middle_name

#Повертає ПІБ
    def get_full_name(self) -> str:
        return f"{self.last_name} {self.first_name} {self.middle_name}"

#Клас, який представляє учня
class Student(Person):
    def __init__(self, last_name: str, first_name: str, middle_name: str,
                 birth_year: int, gender: str, average_grade: float,
                 parallel: int, vertical: str):
        super().__init__(last_name, first_name, middle_name)
        self.birth_year: int = birth_year
        self.gender: str = gender
        self.average_grade: float = average_grade
        self.parallel: int = parallel
        self.vertical: str = vertical

#Метод, щоб вивести інформацію про учня
    def display_info(self) -> None:
        st.write(f"Учень: {self.get_full_name()}, {self.parallel}-{self.vertical}, Оцінка: {self.average_grade:.2f}")

#Клас, який представляє один клас школи
class SchoolClass:
    def __init__(self, parallel: int, vertical: str):
        self.parallel: int = parallel
        self.vertical: str = vertical
        self.students: List[Student] = []  #Інкапсуляція списку учнів

#Повертає повну назву класу, наприклад 8-А
    def get_class_name(self) -> str:
        return f"{self.parallel}-{self.vertical}"

    def get_student_count(self) -> int:
        return len(self.students)

#Метод переведення класу на наступний рік
    def promote_class(self) -> None:
        if self.parallel < 11:
            self.parallel += 1
            for student in self.students:
                student.parallel = self.parallel
        elif self.parallel == 11:
            self.parallel = 12  # 11-й клас "випускається"

#Базовий клас для працівників, тут і спадкування і поліморфізм
class Employee(Person, ABC):
    BASE_SALARIES: Dict[str, float] = {
        'Director': 15000.0, 'Teacher': 12000.0, 'SecurityGuard': 11000.0
    }

    def __init__(self, last_name: str, first_name: str, middle_name: str, position: str):
        super().__init__(last_name, first_name, middle_name)
        self.position: str = position
        self.base_salary: float = self.BASE_SALARIES.get(position, 10000.0)
        self.calculated_salary: Optional[float] = None

#Абстрактний метод для розрахунку зарплати
    @abstractmethod
    def calculate_salary(self) -> float:
        pass

#Клас вчитель
class Teacher(Employee):
    def __init__(self, last_name: str, first_name: str, middle_name: str, pedagogical_experience: int):
        super().__init__(last_name, first_name, middle_name, 'Teacher')
        self.pedagogical_experience: int = pedagogical_experience

#Розрахунок: ставка * пед. стаж / 30
    def calculate_salary(self) -> float:
        exp = self.pedagogical_experience if self.pedagogical_experience > 0 else 1
        return self.base_salary * exp / 30

#Клас Директор(Спадкування від вчителя)
class Director(Teacher):
    def __init__(self, last_name: str, first_name: str, middle_name: str,
                 pedagogical_experience: int, management_experience: int):
        super().__init__(last_name, first_name, middle_name, pedagogical_experience)
        self.position = 'Director'
        self.base_salary = self.BASE_SALARIES.get('Director', 15000.0)
        self.management_experience: int = management_experience

#Розрахунок: ставка * пед. стаж / 50 + стаж керування * 500
    def calculate_salary(self) -> float:
        exp_ped = self.pedagogical_experience if self.pedagogical_experience > 0 else 1
        return (self.base_salary * exp_ped / 50) + (self.management_experience * 500)

#Клас охоронець
class SecurityGuard(Employee):
    def __init__(self, last_name: str, first_name: str, middle_name: str, total_experience: int):
        super().__init__(last_name, first_name, middle_name, 'SecurityGuard')
        self.total_experience: int = total_experience

#Розрахунок: базова ставка + загальний досвід * 250
    def calculate_salary(self) -> float:
        return self.base_salary + (self.total_experience * 250)



#2. ШКОЛА

#Головний клас, що керує сутностями школи та її статистикою
class School:
    def __init__(self, name: str = "Школа №2"):
        self.name: str = name
        self.classes: Dict[str, SchoolClass] = {}

#Завантаження даних в об'єкти
    def load_data_from_csv(self, classes_data: List[Dict[str, Any]], students_data: List[Dict[str, Any]]) -> bool:
        self.classes = {}
        try:
            for row in classes_data:
                self.classes[f"{int(row['parallel'])}-{row['vertical']}"] = SchoolClass(int(row['parallel']),
                                                                                        str(row['vertical']))
        except Exception:
            st.error("Помилка: Неправильний формат у classes.csv.")
            return False

        try:
            for row in students_data:
                class_name = f"{int(row['parallel'])}-{str(row['vertical'])}"
                if class_name in self.classes:
                    student = Student(
                        last_name=row['last_name'], first_name=row['first_name'], middle_name=row['middle_name'],
                        birth_year=int(row['birth_year']), gender=row['gender'],
                        average_grade=float(row['average_grade']),
                        parallel=int(row['parallel']), vertical=str(row['vertical'])
                    )
                    self.classes[class_name].students.append(student)  # Додавання учня
            st.success(f"Успішно завантажено {len(self.classes)} класів та {self.get_total_student_count()} учнів.")
            return True
        except Exception:
            st.error("Помилка: Неправильний формат або відсутні колонки у students.csv.")
            return False

#Фільтрує та повертає лише класи 1-11
    def get_current_classes(self) -> List[SchoolClass]:
        return [cls for cls in self.classes.values() if 1 <= cls.parallel <= 11]

#Повертає єдиний список учнів
    def get_all_students(self) -> List[Student]:
        return [s for cls in self.get_current_classes() for s in cls.students]

    def get_total_student_count(self) -> int:
        return sum(cls.get_student_count() for cls in self.get_current_classes())

#Інформація для статистики
    def get_statistics(self) -> Dict[str, Any]:
        stats: Dict[str, Any] = {'is_valid': False}
        all_students = self.get_all_students()
        current_classes = self.get_current_classes()
        total_students = len(all_students)
        stats['total_students'] = total_students

        if total_students == 0 or not current_classes: return stats
        stats['is_valid'] = True

#Створення статистики
        male_count = sum(1 for s in all_students if s.gender == 'M')
        class_counts = [cls.get_student_count() for cls in current_classes]
        stats['male_percent'] = (male_count / total_students) * 100
        stats['female_percent'] = ((total_students - male_count) / total_students) * 100
        stats['avg_students_per_class'] = sum(class_counts) / len(class_counts)

        max_count, min_count = max(class_counts), min(class_counts)
        stats['max_students'] = max_count
        stats['max_classes'] = ", ".join(
            cls.get_class_name() for cls in current_classes if cls.get_student_count() == max_count)
        stats['min_students'] = min_count
        stats['min_classes'] = ", ".join(
            cls.get_class_name() for cls in current_classes if cls.get_student_count() == min_count)

        return stats

# Відображення статистики в Streamlit
    @staticmethod
    def display_statistics(stats: Dict[str, Any], title: str) -> None:
        st.subheader(f"{title} СТАТИСТИКА ШКОЛИ")
        if not stats.get('is_valid', False):
            st.warning("Недостатньо даних для розрахунку статистики. Будь ласка, завантажте файли.")
            return

        cols = st.columns(3)
        cols[0].metric("Усього учнів", stats.get('total_students', 0))
        cols[1].metric("Середня к-ть учнів/клас", f"{stats.get('avg_students_per_class', 0):.2f}")
        cols[2].metric("Розподіл", f"{stats.get('male_percent', 0):.1f}% / {stats.get('female_percent', 0):.1f}%")

        st.markdown(
            f"* **Макс. учнів:** **{stats.get('max_students', 0)}** (у класах: {stats.get('max_classes', 'N/A')})\n"
            f"* **Мін. учнів:** **{stats.get('min_students', 0)}** (у класах: {stats.get('min_classes', 'N/A')})")

#Генерує та відображає графіки Matplotlib у Streamlit
    def generate_and_display_graphs(self) -> None:
        all_students = self.get_all_students()
        student_data_list = [{'parallel': s.parallel, 'vertical': s.vertical,
                              'birth_year': s.birth_year, 'average_grade': s.average_grade}
                             for s in all_students]

        st.header("Графічна візуалізація даних")
        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)

        #Учні по паралелях
        parallel_counts = {}

        for s in student_data_list:
            p = s['parallel']

            if p in parallel_counts:
                parallel_counts[p] += 1 # Якщо клас уже є, то додаємо 1
            else:
                parallel_counts[p] = 1 # Якщо файлу немає, то створюємо і ставимо 1
        parallels = sorted(parallel_counts.keys())
        counts = [parallel_counts[p] for p in parallels]

        with col1:
            st.subheader("Розподіл учнів по паралелях")
            fig, ax = plt.subplots()
            ax.bar(parallels, counts, color='purple')
            ax.set_xlabel("Паралель")
            ax.set_ylabel("Кількість учнів")
            ax.set_xticks(parallels)
            st.pyplot(fig)

        #Середня кількість по вертикалях
        vertical_stats = {}  # Скільки учнів у кожній вертикалі
        vertical_class_count = {} # Скільки класів у кожній вертикалі
        for cls in self.get_current_classes():
            v = cls.vertical
            count = cls.get_student_count()

            # Додаємо кількість учнів у вертикалі
            if v in vertical_stats:
                vertical_stats[v] += count
            else:
                vertical_stats[v] = count

            # Підраховуємо кількість учнів у вертикалі
            if v in vertical_class_count:
                vertical_class_count[v] += 1
            else:
                vertical_class_count[v] = 1

        #Формуємо списки для графіка
        verticals = sorted(vertical_stats.keys())
        avg_counts = [vertical_stats[v]/vertical_class_count[v] for v in verticals]


        with col2:
            st.subheader("Середня к-ть учнів по вертикалях")
            fig, ax = plt.subplots()
            ax.bar(verticals, avg_counts, color='red')
            ax.set_xlabel("Вертикаль")
            ax.set_ylabel("Сер. кількість учнів")
            st.pyplot(fig)

        birth_year_counts = {}  # словник: рік народження → кількість учнів

        for s in student_data_list:
            year = s['birth_year']

            # якщо рік уже є збільшити лічильник
            if year in birth_year_counts:
                birth_year_counts[year] += 1
            else:
                # якщо немає - створюємо запис
                birth_year_counts[year] = 1

        # формуємо списки для графіка
        years = sorted(birth_year_counts.keys())
        counts_by_year = [birth_year_counts[y] for y in years]

        with col3:
            st.subheader("Учні за роком народження")
            fig, ax = plt.subplots()
            ax.plot(years, counts_by_year, marker='o', linestyle='-', color='black')
            ax.set_xlabel("Рік народження")
            ax.set_ylabel("Кількість учнів")
            ax.set_xticks(years)
            st.pyplot(fig)

        #Scatter: Оцінка vs Паралель
        scatter_x = [s['parallel'] for s in student_data_list]
        scatter_y = [s['average_grade'] for s in student_data_list]

        with col4:
            st.subheader("Середня оцінка учнів vs Паралель")
            fig, ax = plt.subplots()
            ax.scatter(scatter_x, scatter_y, alpha=0.5, color='orange')
            ax.set_xlabel("Паралель")
            ax.set_ylabel("Середня оцінка")
            ax.set_xticks(sorted(list(set(scatter_x))))
            st.pyplot(fig)

#Виконує переведення всіх файлів на рік вперед
    def promote_all_classes(self) -> None:
        st.info("Виконую переведення всіх класів на рік вперед...")
        new_classes_dict = {}
        for x, cls in self.classes.items():
            cls.promote_class()  # Виклик методу об'єкта
            if cls.parallel <= 11:
                new_classes_dict[cls.get_class_name()] = cls
        self.classes = new_classes_dict
        st.success(" Переведення завершено.")



# 3. УТИЛІТИ ТА CSV-РОБОТА

#Читає завантажений CSV-файл у список словників
def read_csv_file(uploaded_file) -> List[Dict[str, Any]]:
    data = []
    content = uploaded_file.getvalue().decode("utf-8")
    reader = csv.DictReader(content.splitlines())
    for row in reader:
        processed_row: Dict[str, Any] = {}
        for key, value in row.items():
            key, value = key.strip(), value.strip()
            # Конвертація в число (int або float)
            if value.replace('.', '', 1).isdigit():
                processed_row[key] = float(value) if '.' in value else int(value)
            else:
                processed_row[key] = value
        data.append(processed_row)
    return data

#Записує список словників у фізичний CSV-файл
def write_csv_file(data: List[Dict[str, Any]], filename: str) -> None:
    if not data: return

    # Збір всіх можливих ключів для уникнення помилки 'dict contains fields not in fieldnames'
    all_keys = set()
    for row in data: all_keys.update(row.keys())

    fieldnames = ['ПІБ', 'Посада', 'Базова Ставка', 'Розрахована Зарплата (грн)', #Створення повного впорядкованого списку
                  'Педагогічний Стаж', 'Стаж Керування', 'Загальний Досвід']

    final_fieldnames = [key for key in fieldnames if key in all_keys]

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=final_fieldnames, restval='', extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)

#Створює програмно об'єкти працівників
def get_employees_data() -> List[Employee]:
    return [
        Director("Іваненко", "Максим", "Олегович", 25, 10),
        Teacher("Савчук", "Вікторія", "Павлівна", 15),
        Teacher("Коваль", "Андрій", "Михайлович", 3),
        SecurityGuard("Гнатюк", "Сергій", "Васильович", 5),
    ]



# 4. СТОРІНКА СЦЕНАРІЮ 1: КЛАСИ ТА УЧНІ

#Сторінка Streamlit для першого сценарію
def page_scenario_1() -> None:
    st.header("Сценарій 1: Статистика, Графіки та Переведення класів")

    if 'school' not in st.session_state:
        st.session_state['school'] = School("Гімназія 'Прогрес'")
        st.session_state['data_loaded'] = False
        st.session_state['promoted'] = False
    school = st.session_state['school']


    st.subheader("1. Завантаження даних")
    st.info("Будь ласка, завантажте ваші **classes.csv** та **students.csv**.")

    classes_file = st.file_uploader("Завантажте classes.csv", type=['csv'], key="classes_uploader")
    students_file = st.file_uploader("Завантажте students.csv", type=['csv'], key="students_uploader")
    can_load = classes_file and students_file

    if can_load and st.button("Ініціалізувати ООП об'єкти", key="load_s1_button"):
        try:
            classes_data, students_data = read_csv_file(classes_file), read_csv_file(students_file)
            st.session_state['data_loaded'] = school.load_data_from_csv(classes_data, students_data)
            st.session_state['promoted'] = False
            st.rerun()
        except Exception as e:
            st.error(f"Помилка завантаження/обробки: {e}. Перевірте формат даних.")

    if st.session_state['data_loaded']:

        stats = school.get_statistics()
        if not st.session_state['promoted']:
            School.display_statistics(stats, "ПОЧАТКОВА")  # Виклик статичного методу
        else:
            School.display_statistics(stats, "ОНОВЛЕНА")  # Теж виклик статичного методу

        school.generate_and_display_graphs()  # Крок 3

        st.subheader("4. Переведення класів")

        if st.button("Перевести класи на рік вперед", key="promote_button"):
            school.promote_all_classes()
            st.session_state['promoted'] = True
            st.rerun()



# 5. СТОРІНКА СЦЕНАРІЮ 2: ЗАРПЛАТИ

#Сторінка Streamlit для другого сценарію
def page_scenario_2() -> None:
    st.header("Сценарій 2: Керування зарплатами працівників")

    employees = get_employees_data()  # Крок 1
    st.subheader("1. Ініціалізовані працівники")

    employees_df = []
    for emp in employees:
        row = {'ПІБ': emp.get_full_name(), 'Посада': emp.position, 'Базова Ставка': emp.base_salary}
        if isinstance(emp, Teacher): row['Педагогічний Стаж'] = emp.pedagogical_experience
        if isinstance(emp, Director): row['Стаж Керування'] = emp.management_experience
        if isinstance(emp, SecurityGuard): row['Загальний Досвід'] = emp.total_experience
        employees_df.append(row)
    st.dataframe(employees_df, hide_index=True)

    st.subheader("2. Розрахунок зарплат") # Поліморфізм

    if st.button("Розрахувати зарплати"):

        salary_data: List[Dict[str, Any]] = []
        for emp in employees:
            salary = emp.calculate_salary()  # Крок 2: Поліморфний виклик
            row = {
                'ПІБ': emp.get_full_name(), 'Посада': emp.position, 'Базова Ставка': emp.base_salary,
                'Розрахована Зарплата (грн)': f"{salary:.2f}"
            }
            if isinstance(emp, Teacher): row['Педагогічний Стаж'] = emp.pedagogical_experience
            if isinstance(emp, Director): row['Стаж Керування'] = emp.management_experience
            if isinstance(emp, SecurityGuard): row['Загальний Досвід'] = emp.total_experience
            salary_data.append(row)

        st.success("Розрахунок завершено.")
        st.dataframe(salary_data, hide_index=True)

        # 3. Збереження таблиці розрахованих зарплат у файл CSV
        try:
            write_csv_file(salary_data, 'salaries.csv')
            with open('salaries.csv', 'rb') as f:
                st.download_button(
                    label="Зберегти таблицю зарплат у salaries.csv (Крок 3)",
                    data=f.read(), file_name='salaries.csv', mime='text/csv',
                )
            st.info("Файл salaries.csv створено та готовий до завантаження.")
        except Exception as e:
            st.error(f"Помилка при записі файлу: {e}. Перевірте права доступу до папки.")



# 6. ГОЛОВНА ФУНКЦІЯ STREAMLIT

#Головна функція, яка відповідає за навігацію між сценаріями
def main():
    st.set_page_config(layout="wide", page_title="Залікова робота: Школа")
    st.sidebar.title("Навігація")

    selected_page = st.sidebar.radio(
        "Оберіть сценарій для виконання:",
        ("Сценарій 1: Класи та Учні", "Сценарій 2: Зарплати Працівників")
    )

    st.title("Залікова робота з програмування: Керування школою")

    if selected_page == "Сценарій 1: Класи та Учні":
        page_scenario_1()
    elif selected_page == "Сценарій 2: Зарплати Працівників":
        page_scenario_2()


if __name__ == "__main__":
    main()