import math

class Circulo:
  @staticmethod
  def calcular_area(radio: float) -> float:
    return math.pi * radio ** 2

  @staticmethod
  def calcular_circunferencia(radio: float) -> float:
    return 2 * math.pi * radio


def main():
  radio = float(input("Ingrese el radio del círculo: "))
  
  area = Circulo.calcular_area(radio)
  circunferencia = Circulo.calcular_circunferencia(radio)
  
  print(f"Área del círculo: {area}")
  print(f"Longitud de la circunferencia: {circunferencia}")


if __name__ == "__main__":
  main()
