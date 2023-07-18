import numpy as np

from typing import Optional, Union


class Solver:
    CAPITAL = 240
    OPTIONS = [
        "Ampliação da capacidade do armazém ZDP em 5%",
        "Ampliação da capacidade do armazém MGL em 7%",
        "Compra de empilhadeira",
        "Projeto de P&D I",
        "Projeto de P&D II",
        "Aquisição de novos equipamentos",
        "Capacitação de funcionário",
        "Ampliação da estrutura de carga rodoviária",
        "Construção de datacenter",
        "Aquisição de empresa concorrente",
        "Compra de serviços em nuvem",
        "Criação de aplicativo mobile e desktop",
        "Terceirizar serviço de otimização da logística"
    ]
    INITIAL_SOLUTION = ""
    COSTS = [47, 40, 17, 27, 34, 23, 5, 44, 32, 80, 12, 15, 30]
    RETURNS = [41, 33, 14, 25, 32, 32, 9, 19, 12, 45, 8, 12, 38]
    RISCS = [1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 1, 1, 2]
    MIN_RISCS = [2, 2, 1]
    MAX_COST_PER_RISC = [120, 150, 90]

    _current_best_solution: Optional[str] = None
    _current_best_solution_return: float = 0
    _current_best_solution_cost: float = float('inf')

    def _get_formated_value(self, value: float):
        return f"R$ {format(value, '.2f')}"

    def _get_total_return(self, solution: str) -> float:
        total = 0
        for i in range(len(solution)):
            if solution[i] == "1":
                total += self.RETURNS[i]
        return total

    def _get_total_cost(self, solution: str) -> float:
        total = 0
        for i in range(len(solution)):
            if solution[i] == "1":
                total += self.COSTS[i]
        return total

    def _satisfy_conditions(self, solution: str) -> Union[bool, int]:
        total_riscs = np.zeros(len(self.MIN_RISCS))
        total_costs_per_risc = np.zeros(len(self.MIN_RISCS))
        total_cost = 0

        for i in range(len(solution)):
            if solution[i] == "1":
                index = self.RISCS[i] - 1
                total_riscs[index] += 1
                total_costs_per_risc[index] += self.COSTS[i]
                total_cost += self.COSTS[i]

                if total_cost > self.CAPITAL:
                    return False, -1

                if total_costs_per_risc[index] > self.MAX_COST_PER_RISC[index]:
                    return False, -2

        for i in range(len(total_riscs)):
            if total_riscs[i] < self.MIN_RISCS[i]:
                return False, 1

        return True, 0

    def get_solution(self, solution: str = "", pos: int = 0):
        ok, reason = self._satisfy_conditions(solution)
        if ok:
            total_return = self._get_total_return(solution)
            total_cost = self._get_total_cost(solution)
            if total_return > self._current_best_solution_return or \
                    (total_return == self._current_best_solution_return and total_cost < self._current_best_solution_cost):
                self._current_best_solution = solution
                self._current_best_solution_return = total_return
                self._current_best_solution_cost = total_cost

        if reason >= 0:
            if pos < len(self.OPTIONS):
                self.get_solution(solution + "1", pos + 1)
                self.get_solution(solution + "0", pos + 1)

    def get_formated_solution(self, solution: str):
        total_riscs = np.zeros(len(self.MIN_RISCS))
        total_costs_per_risc = np.zeros(len(self.MIN_RISCS))
        total_return_per_risc = np.zeros(len(self.MIN_RISCS))
        total_cost = 0
        total_return = 0

        for i in range(len(solution)):
            if solution[i] == "1":
                index = self.RISCS[i] - 1
                total_riscs[index] += 1
                total_costs_per_risc[index] += self.COSTS[i]
                total_return_per_risc[index] += self.RETURNS[i]
                total_cost += self.COSTS[i]
                total_return += self.RETURNS[i]

        selected_options = ""
        for i in range(len(solution)):
            if solution[i] == "1":
                selected_options += self.OPTIONS[i] + "\n"

        return f"""
## QUANTIDADE DE OPÇÕES POR RISCO
Baixo: {total_riscs[0]}
Médio: {total_riscs[1]}
Alto: {total_riscs[2]}

## TOTAL (R$) DE CUSTO POR RISCO
Baixo: {self._get_formated_value(total_costs_per_risc[0] * 1e4)}
Médio: {self._get_formated_value(total_costs_per_risc[1] * 1e4)}
Alto: {self._get_formated_value(total_costs_per_risc[2] * 1e4)}

## TOTAL (R$) DE RETORNO POR RISCO
Baixo: {self._get_formated_value(total_costs_per_risc[0] * 1e4)}
Médio: {self._get_formated_value(total_costs_per_risc[1] * 1e4)}
Alto: {self._get_formated_value(total_costs_per_risc[2] * 1e4)}

## CUSTO (R$) DE INVESTIMENTO
{self._get_formated_value(total_cost * 1e4)}

## RETORNO TOTAL (R$) DE INVESTIMENTO ESPERADO
{self._get_formated_value(total_return * 10e3)}

## OPÇÕES ESCOLHIDAS
{selected_options}

{solution}
"""


def main():
    solver = Solver()
    solver.get_solution()
    print(solver.get_formated_solution(solver._current_best_solution))


if __name__ == "__main__":
    main()
