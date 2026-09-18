class Edades:
  @staticmethod
  def calcular_edad_alber(edjuan: float) -> float:
    return 2 * edjuan / 3

  @staticmethod 
  def calcular_edad_ana(edjuan: float) -> float:
    return 4 * edjuan / 3
  
  @staticmethod 
  def calcular_edad_mama(edjuan: float, edalber: float, edana: float) -> float:
    return edjuan + edalber + edana
  
  
def main():
  edjuan = float(input("How old is Juan?"))
  edalber = Edades.calcular_edad_alber(edjuan)
  edana = Edades.calcular_edad_ana(edjuan)
  edmama = Edades.calcular_edad_mama(edjuan, edalber, edana)
  
  print(f"La edad de la mamá es: {edmama}") 
  print(f"La edad de Juan es: {edjuan}")
  print(f"La edad de Alber es: {edalber}")
  print(f"La edad de Ana es: {edana}")  


if __name__ == "__main__":
  main()