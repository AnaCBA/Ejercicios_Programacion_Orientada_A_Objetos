class Salario:
  @staticmethod
  def calcular_salario_bruto(horas_trabajadas: float, valor_hora: float) -> float:
    return horas_trabajadas * valor_hora

  @staticmethod
  def calcular_retencion(salario_bruto: float, porcentaje_retencion: float) -> float:
    return salario_bruto * porcentaje_retencion / 100
  
  @staticmethod
  def calcular_salario_neto(salario_bruto: float, retencion: float) -> float:
    return salario_bruto - retencion


def main():
  horas = 48
  valor_hora = 5000
  porcentaje_retencion = 12.5
  
  salario_bruto = Salario.calcular_salario_bruto(horas, valor_hora)
  retencion = Salario.calcular_retencion(salario_bruto, porcentaje_retencion)
  salario_neto = Salario.calcular_salario_neto(salario_bruto, retencion)
  
  print(f"Salario bruto: ${salario_bruto}")
  print(f"Retención en la fuente (12.5%): ${retencion}")
  print(f"Salario neto: ${salario_neto}")


if __name__ == "__main__":
  main()
