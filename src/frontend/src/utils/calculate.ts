export function compare(a: number, b: number, operator: string) {
  if (operator === "==") return a == b;
  else if (operator === "===") return a === b;
  else if (operator === "!=") return a != b;
  else if (operator === "!==") return a !== b;
  else if (operator === ">") return a > b;
  else if (operator === ">=") return a >= b;
  else if (operator === "<") return a < b;
  else if (operator === "<=") return a <= b;
  else throw "Unknown operator";
}
export function calculate(a: number, b: number, operator: string) {
  if (operator === "+") return a + b;
  else if (operator === "-") return a - b;
  else if (operator === "*") return a * b;
  else if (operator === "/") return a / b;
  else if (operator === "%") return a % b;
  else throw "Unknown operator";
}
