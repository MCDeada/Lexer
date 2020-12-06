class FSM:
    # Переменная где ключом будет состояние, а значение: [символ перехода, следующее состояние]
    rules = {}
    start_state = 0
    current_state = 0
    final_state = 0

    def load_rules(self, filename):
        t = open(filename)
        start_final_states_row = t.readline()[:-1] # Строка без символа переноса
        lst = start_final_states_row.split()
        self.start_state = lst[0]
        self.final_state = lst[1]
        self.current_state = lst[0]
        while True: # Условие остановки внутри
            row = t.readline()[:-1]
            if len(row) == 0: # Проверка на конец считывания
                break
            cur_state_pos = row.find(':')
            cur_state = row[:cur_state_pos] # состояние из которого начинается переход
            row = row[cur_state_pos + 2:]
            transition_symbol_pos = row.find('/')
            transition_symbol = row[:transition_symbol_pos] # символ перехода
            next_state = row[transition_symbol_pos + 1:] # состояние, в которое перешли
            if self.rules.get(cur_state) == None:
                self.rules[cur_state] = [transition_symbol, next_state]
            else:
                self.rules[cur_state] += [transition_symbol, next_state]
        t.close() # Закрываем файл

def MaxString(FSM, st, k):
    res_str = ''
    res_str_max = ''
    rules = FSM.rules
    used_rule = False
    i = k
    while i < len(st):
        used_rule = False
        avaliable_rules = rules.get(FSM.current_state) # Выбираем доступные из текущего состояния правила
        if avaliable_rules == None: # Если на предыдущем шаге пришли в конечное состояние,
                                    # тот правил не будет у конечного автомата
            if len(res_str) > len(res_str_max):
                res_str_max = res_str
            res_str = ''
            FSM.current_state = FSM.start_state
            avaliable_rules = rules.get(FSM.current_state)
        for j in range(0, len(avaliable_rules), 2):
            if st[i] == avaliable_rules[j]:
                used_rule = True
                FSM.current_state = avaliable_rules[j + 1]
                res_str += st[i]
                break
        # Если ни одно правило не подошло
        # Значит превалась начатая последовательность
        if not used_rule:
            i -= len(res_str)
            res_str = ''
            FSM.current_state = FSM.start_state
        i += 1
    # Если терминальная последовательность замыкала строку, то она
    # остается непроверена на максимальность      
    if FSM.current_state == FSM.final_state:
        if len(res_str) > len(res_str_max):
            res_str_max = res_str
            res_str = ''
    if len(res_str_max):
        return [True, res_str_max]
    else:
        return [False, res_str_max]

# 'asdc' = asdc <True, 4>
# 'asd' = <False, 0>
# 'samsamsung fgws h asdc'  = samsung <True, 7>
# 'asdcsamsamsung fgw'  = samsung <True, 7>
# 'samsamsung fgws h asdc'  = asdc <True, 4> если k = 5
# 'asdcsamsamsung fgw'  = samsung <True, 7> если k = 5
# 'asdcsamsamsung fgw'  = <False, 0> если k = 10

if __name__ == "__main__":
    FSM_1 = FSM()
    FSM_1.load_rules('FSM_task1_finite.txt')
    while True:
        st = input('enter string\n')
        if st == 'exit':
            break
        FSM_1.current_state = FSM_1.start_state
        lst = MaxString(FSM_1, st, 0)
        if lst[0]:
            print('<', lst[0], ', ', len(lst[1]), '>')
            print('Found string:', lst[1])
        else:
            print('<', lst[0], ', 0>')