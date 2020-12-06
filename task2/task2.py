class FSM:
    # Конструктор
    def __init__(self, filename, second_separator, priority, class_name):
        self.rules = {} # Переменна, где ключ - текущее состояние,
                        # значение: [символ перехода, следующее состояние, символ перехода, следующее состояние, ...]
        self.start_state = 0
        self.current_state = 0
        self.final_state = 0
        self.priority = 0 # Приоретет автомата для разрешения конфликтов
        self.class_name = '' # Имя класса при выводе в файл
        t = open(filename)
        # Форматы файлов задания автоматов:
        # В первой строке начальное состоние и через пробел конечное состояние
        # Последующие строки содержат правила перехода, где сначала идет текущее состояние,
        # потом символ перехода, потом следующеее состояние
        start_final_states_row = t.readline()[:-1] # Строка без символа переноса
        lst = start_final_states_row.split() # Разбиваем в список
        self.start_state = lst[0]
        self.final_state = lst[1]
        self.current_state = lst[0]
        self.priority = priority
        self.class_name = class_name
        while True: # Условие остановки внутри
            row = t.readline()[:-1]
            if len(row) == 0: # Проверка на конец считывания
                break
            cur_state_pos = row.find(':')
            cur_state = row[:cur_state_pos] # состояние из которого начинается переход
            row = row[cur_state_pos + 2:]
            transition_symbol_pos = row.find(second_separator)
            transition_symbol = row[:transition_symbol_pos] # символ перехода
            next_state = row[transition_symbol_pos + 1:] # состояние, в которое перешли
            if self.rules.get(cur_state) == None:
                self.rules[cur_state] = [transition_symbol, next_state]
            else:
                self.rules[cur_state] += [transition_symbol, next_state]
        t.close() # Закрываем файл

# Функция поиска максимальной терминальной последовательности символов в строке для автомата
def MaxString(FSM, st, k):
    res_str = ''
    rules = FSM.rules # Правила автомата
    prev_state = FSM.current_state # Предыдущее состояние
    result = []
    for i in range(k, len(st)):
        avaliable_rules = rules.get(FSM.current_state) # Выбираем доступные из текущего состояния правила
        used_rule = False # Флаг того, что к текущему символу подошло хоть какое-то правило из доступных
        for j in range(0, len(avaliable_rules), 2):
            if st[i] == avaliable_rules[j]:
                used_rule = True
                prev_state = FSM.current_state
                FSM.current_state = avaliable_rules[j + 1]
                res_str += st[i]
                # У идентификаторов и чисел переход в конечное состояние ничего не значит
                if FSM.class_name != 'identificator' and FSM.class_name != 'number':
                    if FSM.current_state == FSM.final_state and prev_state != FSM.final_state:
                        # Добавляется найденная строка, индекс её начала в строке st и индекс её окончания в st
                        result.append([res_str, i - len(res_str) + 1, i + 1]) 
                        res_str = ''
                        FSM.current_state = FSM.start_state
                        prev_state = FSM.current_state
                break
        # Если на протяжении нескольких символов used_rule было true и резко стало false,
        # значит идентификатор найдет, та же логика для чисел.
        # К сожалению, такая ситуация не позволит считать идентификатор или число, 
        # если за ними не идет еще один любой символ не подходящий под правило.
        if not used_rule and FSM.class_name == 'identificator':
            if len(res_str):
                result.append([res_str, i - len(res_str), i])
        if not used_rule and FSM.class_name == 'number':
            if len(res_str):
                result.append([res_str, i - len(res_str), i])
        # Если правило для текущего символа не было найдено, значит это конец какой-то последовательности,
        # и надо вернуть автомат в исходное состояние
        if not used_rule:
            FSM.current_state = FSM.start_state
            prev_state = FSM.current_state
            res_str = ''
    # Вывод
    if len(result):
        return [True, FSM.class_name, FSM.priority, result]
    else:
        return [False, FSM.class_name, FSM.priority, result]

# Функция, использованная для отладки. Проверка отдельных строк
def check_str(FSM, k):
    print('enter string')
    while True:
        st = input()
        if st == 'exit':
            break
        FSM.current_state = FSM.start_state
        lst = MaxString(FSM, st, k)
        print('<', lst[0], ', ', len(lst[1]), '>')

# Функция вычисляющая поток лексем
def analyse(filename, FSMs):
    f = open(filename)
    end_results = '' # строка для записи в output.txt
    while True:
        results = [] 
        row = f.readline()[:-1:] # Читаем строку без \n
        row = row.replace('	', '') # Удаляем символы \t с начала
        if len(row) == 0:
            break
        for i in range(len(FSMs)): # Получаем информацию обо всех видах лексем
            FSMs[i].current_state = FSMs[i].start_state
            lst = MaxString(FSMs[i], row, 0)
            results.append(lst)
        i_next = 0
        # Так как у каждое найденная строка содержит индекс начала
        # Можно тогда на каждый индекс начала найти кандидатов и 
        # выбрать из них с наибольшей длиной или самого приоритетного
        # и перейти на начало следующего элемента
        while i_next < len(row):
            candidates = []
            for i in range(len(results)):
                if results[i][0]:
                    lst = results[i][3]
                    for j in range(len(lst)):
                        if lst[j][1] == i_next:
                            candidates.append([results[i][1], results[i][2], lst[j][0]])
            max_str = candidates[0][2]
            max_priority = candidates[0][1]
            max_type = candidates[0][0]
            for i in range(1, len(candidates)):
                if len(candidates[i][2]) > len(max_str):
                    max_str = candidates[i][2]
                    max_priority = candidates[i][1]
                    max_type = candidates[i][0]
                elif len(candidates[i][2]) == len(max_str) and candidates[i][1] < max_priority:
                    max_str = candidates[i][2]
                    max_priority = candidates[i][1]
                    max_type = candidates[i][0]
            end_results += '<' + max_str + ', ' + max_type + '>\n'
            i_next += len(max_str)
    f.close()
    # Запись в файл
    with open('output.txt', 'w') as f:
        f.write(end_results)
    

if __name__ == "__main__":
    # Блок инициализации автоматов
    #---------------------------------------------------------------------
    FSMs = []
    FSMs.append(FSM('FSM_alg_operators.txt',        ' ', 2, 'algorithmic_operator'))
    FSMs.append(FSM('FSM_assignment_operators.txt', ' ', 3, 'assignment_operator'))
    FSMs.append(FSM('FSM_brackets.txt',             ' ', 1, 'bracket'))
    FSMs.append(FSM('FSM_compare_operators1.txt',   ' ', 3, 'compare_operator'))
    FSMs.append(FSM('FSM_compare_operators2.txt',   ' ', 2, 'compare_operator'))
    FSMs.append(FSM('FSM_identificators.txt',       ' ', 2, 'identificator'))
    FSMs.append(FSM('FSM_keywords.txt',             ' ', 1, 'keyword'))
    FSMs.append(FSM('FSM_logic_operators.txt',      ' ', 3, 'logic_operator'))
    FSMs.append(FSM('FSM_separators.txt',           '.', 2, 'separator'))
    FSMs.append(FSM('FSM_types.txt',                ' ', 1, 'type'))
    FSMs.append(FSM('FSM_numbers1.txt',             ' ', 1, 'number'))
    FSMs.append(FSM('FSM_numbers1_1.txt',           ' ', 1, 'number'))
    FSMs.append(FSM('FSM_numbers2.txt',             ' ', 1, 'number'))
    FSMs.append(FSM('FSM_numbers3.txt',             ' ', 1, 'number'))
    FSMs.append(FSM('FSM_numbers3_1.txt',           ' ', 1, 'number'))
    #---------------------------------------------------------------------
    analyse('input.txt', FSMs)