# Projet de Simulation d'Algorithme Génétique

Ce projet implémente une simulation d'algorithme génétique pour optimiser les paramètres d'un robot évoluant dans un environnement avec des obstacles, de la nourriture et de l'eau. Le robot utilise des capteurs pour détecter les objets et ajuster son comportement en conséquence.

## Structure du Répertoire

- `AlgoGenetique.py` : Contient l'implémentation de l'algorithme génétique.
- `myclass.py` : Définit les classes pour les objets de l'environnement, les capteurs et le robot.
- `world_env.py` : Gère l'exécution visuelle de la simulation et l'affichage des résultats.
- `data/` : Contient les fichiers de données, y compris les statistiques de fitness et les vidéos générées.
- `environment.yml` : Fichier de configuration pour créer l'environnement Conda nécessaire à l'exécution du projet.
- `Genetic_Sceme.md` : Documentation sur les paramètres utilisés dans l'algorithme génétique.
- `.gitignore` : Fichier pour ignorer les fichiers de cache Python et autres fichiers non pertinents.

## Prérequis

- Python 3.11
- Conda

## Installation

1. Clonez le dépôt :

   ```sh
   git clone <URL_DU_DEPOT>
   cd <NOM_DU_DEPOT>
   ```

2. Créez un environnement Conda :

   ```sh
   conda env create -f envconda.yml
   conda activate envconda
   ```

## Utilisation

Pour exécuter la simulation visuelle avec les paramètres par défaut :

```sh
python world_env.py
```

## Description des Fichiers

### [`AlgoGenetique.py`](AlgoGenetique.py)

Ce fichier contient la classe [`GeneticAlgorithm`](../../../../../j:/Master/S3/IAR/PROJET_IAR/AlgoGenetique.py) qui implémente les méthodes suivantes :

- [`initialize_population()`](../../../../../j:/Master/S3/IAR/PROJET_IAR/AlgoGenetique.py)
- [`random_individual()`](../../../../../j:/Master/S3/IAR/PROJET_IAR/AlgoGenetique.py)
- [`evaluate_fitness()`](../../../../../j:/Master/S3/IAR/PROJET_IAR/AlgoGenetique.py)
- [`crossover()`](../../../../../j:/Master/S3/IAR/PROJET_IAR/AlgoGenetique.py)
- [`mutate()`](../../../../../j:/Master/S3/IAR/PROJET_IAR/AlgoGenetique.py)
- [`select_parents()`](../../../../../j:/Master/S3/IAR/PROJET_IAR/AlgoGenetique.py)
- [`parallel_evaluate_fitness()`](../../../../../j:/Master/S3/IAR/PROJET_IAR/AlgoGenetique.py)
- [`evolve()`](../../../../../j:/Master/S3/IAR/PROJET_IAR/AlgoGenetique.py)
- [`get_best_individual()`](../../../../../j:/Master/S3/IAR/PROJET_IAR/AlgoGenetique.py)
- [`save_fitness_stats()`](../../../../../j:/Master/S3/IAR/PROJET_IAR/AlgoGenetique.py)

### [`myclass.py`](myclass.py)

Ce fichier définit plusieurs classes :

- [`Object`](../../../../../j:/Master/S3/IAR/PROJET_IAR/myclass.py) : Représente les objets de l'environnement (nourriture, eau, pièges).
- [`SensorimotorLink`](../../../../../j:/Master/S3/IAR/PROJET_IAR/myclass.py) : Représente les liens sensorimoteurs du robot.
- [`Sensor`](../../../../../j:/Master/S3/IAR/PROJET_IAR/myclass.py) : Représente les capteurs du robot.
- [`Robot`](../../../../../j:/Master/S3/IAR/PROJET_IAR/myclass.py) : Représente le robot et gère son comportement.

### [`world_env.py`](world_env.py)

Ce fichier gère l'exécution visuelle de la simulation. Les principales fonctions sont :

- [`visual_execution()`](../../../../../j:/Master/S3/IAR/PROJET_IAR/world_env.py)
- [`ask_to_continue()`](../../../../../j:/Master/S3/IAR/PROJET_IAR/world_env.py)
- [`visualise_fitness_stats()`](../../../../../j:/Master/S3/IAR/PROJET_IAR/world_env.py)
- [`transfer_function()`](../../../../../j:/Master/S3/IAR/PROJET_IAR/myclass.py)
- [`visualise_tranfer_fonction()`](../../../../../j:/Master/S3/IAR/PROJET_IAR/world_env.py)
- [`genetic_execution()`](../../../../../j:/Master/S3/IAR/PROJET_IAR/world_env.py)
- [`main()`](../../../../../j:/Master/S3/IAR/PROJET_IAR/world_env.py)
