# Solar Eclipse Photography

<hr style="height:8px; border:none; background-color:red;">

> [!CAUTION]
> ## ⚠️ DANGER CRITIQUE : RISQUE DE CÉCITÉ ⚠️
> **CE SYSTÈME EST EXCLUSIVEMENT RÉSERVÉ À L'ASTROPHOTOGRAPHIE.**
> 
> * **INTERDICTION FORMELLE** d'utiliser ce dispositif pour l'observation visuelle (œil à l'oculaire).
> * Une défaillance logicielle, un bug du script ou une coupure de courant peut entraîner le retrait imprévu du filtre.
> * L'observation directe du soleil sans filtre à travers un instrument optique provoque une **perte de vue immédiate et définitive**.
> 
> **L'utilisateur assume l'entière responsabilité de l'utilisation de ce code.**

![Danger](https://img.shields.io/badge/DANGER-EYE_SAFETY-red?style=for-the-badge)
![Photo Only](https://img.shields.io/badge/Usage-Astrophotography_Only-blue?style=for-the-badge)

<hr style="height:8px; border:none; background-color:red;"> 

## Solar Eclipse Photography

Ce programme permet d'automatiser la photographie d'une éclipse Solaire ou Lunaire.  
L'objectif est que le cycle de photographies se déroule de manière autonome et permette à l'observateur de vivre pleinement l'évennement.
Pour cela le programme va orchestrer le déclenchement de prises de vues suivant une séquence prédéfinie. Cette séquence est décrite dans un fichier texte.  
Le document ci-après vous explique comment utiliser ce programme est préparer votre observation.  
Ce programme python fonctionne sur une Raspberry sous Linux. Il utilise la librairie Gphoto2 et est normalement compatible avec tous les type de boitiers reconnus par cette librairie.  
Il a été testé avec un Canon 6D et un R6.  

## Principe de fonctionnement

Le programme va réaliser une série d'opération décrites dans le fichier séquence (script).
Les heures peuvent être indiquées en fonction de circonstances locales, 1er contact, 2éme contact...  
Elles peuvent être indiquées aussi en absolue, 13h45m06s...  
Le programme ne gère pas le jour, la séquence commencera à l'heure indiquée quel que soit le jour.
Le nom du fichier script est passé en paramêtre au lancement du programme. 

## Descriptif de la séquence

La séquence de photos est décrite dans un fichier texte.  
Chaque séquence est décrite sur une ligne composée de paramètres séparés par une virgule "," ou un double point ":".
Il faut respecter les règles suivantes

* Pas de paramètre vide, y mettre un "-"
* \# pour commenter une ligne
* Les séquences doivent se suivre temporellement. Le fichier n'est lu que dans un sens. 

Six types de lignes sont possibles, Verif, Config, Boucle, Photo, Interval, Filter.

---
## Syntaxe de la ligne Verif
![Static Badge](https://img.shields.io/badge/text-under%20construction-orange)

Quatre paramètres du boitier sont analysés au démarrage du programme et affichés si une ligne Verif est présente dans le descriptif.  
Il est possible de les rendre bloquants si une valeur est indiquée dans la ligne Verif.  
Si la valeur est - le paramètre n'est pas vérifié. Si la valeur est indiquée la vérification est faite.
Les paramètres ne sont vérifiés qu'au début du cycle.

### Description des champs

Position|Nom|Valeur|Description
:---:|:---:|:---:|:---
1|Action|Verif|Ligne d'activation de la vérification
2|Mode|- ou 3|Le mode manuel est obligatoire sa valeur est 3 (*)
3|Autofocus|- ou 0|L'autofocus doit être désactivé = 0
4|Batterie|- ou N|Indiquer le niveau minimum de batterie en %
5|Stockage|- ou N|Indiquer l'espace minimum en méga octets

### Exemple

Verif : Mode M, AF Off, 20%, 4000M°  
`Verif,3,0,20,4000`


## Syntaxe de la ligne Config 🕔 

La ligne Config permet de travailler en mode heure relative.
En spécifiant les circonstances locales il n'est pas nécessaire de modifier l'ensemble du fichier quand celles-ci changent.
La ligne décrit la config de la manière suivante :

```
       C1    C2    Max   C3    C4
Config,H:M:S,H:M:S,H:M:S,H:M:S,H:M:S
```

### Description des champs

Position|Nom|Valeur|Description
:---:|:---:|:---:|:---
1|Action|Config|Ligne de définition des circonstances locales de l'éclipse
2.1|Hd|0-23|Heure du premier contact C1
2.2|Md|0-59|Minute du premier contact 
2.3|Sd|0-59|Seconde du premier contact
3.1|Hd|0-23|Heure du deuxième contact C2
3.2|Md|0-59|Minute du deuxième contact
3.3|Sd|0-59|Seconde du deuxième contact
4.1|Hd|0-23|Heure du maximum Max
4.2|Md|0-59|Minute du maximum
4.3|Sd|0-59|Seconde du maximum
5.1|Hd|0-23|Heure du troisième contact C3
5.2|Md|0-59|Minute du troisième contact
5.3|Sd|0-59|Seconde du troisième contact
6.1|Hd|0-23|Heure du quatrième contact C4
6.2|Md|0-59|Minute du quatrième contact
6.3|Sd|0-59|Seconde du quatrième contact
| | |

#### Exemple

Config : C1 = 14h41m05s C2 = 16h02m49s Max = 16h03m53s C3 = 16h04m58s C4 = 17h31m03s TestMode = actif   
>Config,14:41:05,16:02:49,16:03:53,16:04:58,17:31:03

---

## Syntaxe de la ligne Photo 📷

L'action Photo réalise une photo à l'heure voulue et avec les paramètres indiqués dans la ligne.
Les heures peuvent être indiquées en mode absolu ou relatif.

### Description des champs Photo

Position|Nom|Valeur|Description
:---:|:---:|:---:|:---
1|Action|Photo|photo unique 
2|Ref|C1,C2,Max,C3,C4 ou -|Indique le point de référence, mettre un "-" si en mode absolu
3|Oper|+ ou -|Ajoute ou soustrait l'heure de début à la Ref
4.1|Hd|0-23|Heure de début de la séquence
4.2|Md|0-59|Minute de début de la séquence
4.3|Sd|0-59|Seconde de début de la séquence
5|Aperture|Diaph.|Valeur du Diaphragme (2.8,8,11...)(*)
6|ISO|Num.|Sensibilité du capteur (100, 800, 6400,...)(*)
7|ShutterSpeed|Num.|Vitesse d'exposition en seconde (*) 
8|MLUDelay|Num.|Délais d'attente entre la montée du mirroir et le déclenchement, en miliseconde. Si 0 pas de montée du mirroir avant le déclenchement. 
|||

(*) Attention prendre des valeurs compatibles avec votre équipement.

### Exemples de ligne Photo

Mode absolu, photo à 21:22:40, Diaph=4, ISO=1600, Vitesse 1, Mirror lockup avec 0,5s de délais.
>`Photo,-,-,21:22:40,4,1600,1,500`

Mode relatif photo 01:10:30 avant C1, Diaph=4, ISO=1600, Vitesse 1, Mirror lockup avec 0,5s de délais.
>`Photo,C1,-,01:10:30,4,1600,1,500`

---

## Syntaxe des lignes Boucle et Interval 🔁


L'action Boucle réalise une série de photos entre l'heure de début et l'heure de fin avec un intervalle donné.

L'action Interval est identique à Boucle mais on indique le nombre de photos au lieu de l'intervalle. L'intervalle entre deux photos est calculé par la durée divisée par le nombre de photos. A cause des arrondis il est possible que le nombre de photos réalisées soit légèrement différent de celui voulu.

Les heures peuvent être indiquées en mode absolu ou relatif.

### Syntaxe en heure absolue

En heure absolue, l'image ou la séquence sera réalisée à l'heure indiqué littéralement.
Chaque ligne décrit une séquence de la manière suivante :

`Action,-,-,Hd:Md:Sd,-,Hf:Mf:Sf,Interval,Aperture,ISO,ShutterSpeed,MLUDelay`

### Syntaxe en heure relative

En heure relative, l'image ou la séquence sera réalisée en fonction de la circonstance locale, de l'opérande et de l'heure indiquée.
Chaque ligne décrit une séquence de la manière suivante :

`Action,C1,+,Hd:Md:Sd,+,Hf:Mf:Sf,Interval,Aperture,ISO,ShutterSpeed,MLUDelay`

### Description des champs Boucle et Interval

Position|Nom|Valeur|Description
:---:|:---:|:---:|:---
1|Action|Boucle, Interval|Suite de photos identiques, photo unique ou déplacement du filtre 
2|Ref|C1,C2,Max,C3,C4 ou -|Indique le point de référence, mettre un "-" si en mode absolu
3|Oper|+ ou -|Ajoute ou soustrait l'heure de début à la Ref
4.1|Hd|0-23|Heure de début de la séquence
4.2|Md|0-59|Minute de début de la séquence
4.3|Sd|0-59|Seconde de début de la séquence
5|Oper|+ ou -|Ajoute ou soustrait l'heure de fin à la Ref
6.1|Hf|0-23|Heure de fin de la séquence (*)
6.2|Mf|0-59|Minute de fin de la séquence (*)
6.3|Sf|0-59|Seconde de fin de la séquence (*)
7|Interval ou Number|Num. >= 1|Intervalle entre deux photos en seconde (*) ou nombre de photo à faire entre Hd et Hf
8|Aperture|Diaph.|Valeur du Diaphragme (2.8,8,11...)(**)
9|ISO|Num.|Sensibilité du capteur (100, 800, 6400,...)(**)
10|ShutterSpeed|Num.|Vitesse d'exposition en seconde (**)
11|MLUDelay|Num.|Délais d'attente entre la montée du mirroir et le déclenchement, en miliseconde. Si 0 pas de montée du mirroir avant le déclenchement. 

(*) Uniquement utilisé par l'action "Boucle" et "Interval".  
(**) Attention prendre des valeurs compatibles avec votre équipement.

#### Exemples

Mode absolu, série de 21:22:05 à 21:25:35, une photo toutes les 5s, Diaph=8, ISO=200, Vitesse 1/2000, pas de Mirror lockup.  
>`Boucle,-,-,21:22:05,-,21:25:35,5,8,200,0.0005,0`

Mode relatif, série de 00:20:00 avant C2 à 00:01:30 après C2, une photo toutes les 5s, Diaph=8, ISO=200, Vitesse 1/2000, pas de Mirror lockup.  
>`Boucle,C2,-,00:20:00,+,00:01:30,5,8,200,0.0005,0`

Mode relatif, série de 200 photos entre 00:20:00 avant C2 et 00:01:30 après C2, Diaph=8, ISO=200, Vitesse 1/2000, pas de Mirror lockup.  
>`Interval,C2,-,00:20:00,+,00:01:30,200,8,200,0.0005,0`

Ligne de commentaire.  
>`# Commentaire`  


### Attention !

Le passage du changement de jour n'est pas fonctionnel dans cette version.  
Utiliser l'heure locale, il y a rarement des éclipses à 0h TL.  
Le temps minimum entre deux images est de 1s.

---

## Syntaxe de la ligne Filter

L'action Filter positionne ou enlève un filtre devant l'objectif. Elle s'appuie sur une adaptation d'un Automatic Flat Panel de la marque Gemini.  
Seule l'heure de début est utilisée.  
Attention à tenir compte du temps de déplacement du filtre. Il faut le prévoir dans votre timing

### Description des champs Filter

Position|Nom|Valeur|Description
:---:|:---:|:---:|:---
1|Action|Filter|Déplacement du filtre 
2|Ref|C1,C2,Max,C3,C4 ou -|Indique le point de référence, mettre un "-" si en mode absolu
3|Oper|+ ou -|Ajoute ou soustrait l'heure de début à la Ref
4.1|Hd|0-23|Heure de début de la séquence
4.2|Md|0-59|Minute de début de la séquence
4.3|Sd|0-59|Seconde de début de la séquence
5|Act|0 ou 1|1 => ouvre, 0 => ferme
|||

## Lancement de la séquence

## Paramétrage du boitier

Le boitier doit être en mode :

* Auto power off à Disable
* Mode Manuel
* Auto Focus en off

## Mirror Lockup
![Static Badge](https://img.shields.io/badge/text-under%20construction-orange)

Si le boitier le permet il est possible d'utiliser le Mirrorlockup. Cela permet d'éviter des vibrations pendant la prise de vue.  


# Configurations

## Mode test

Pour tester le script il est possible d'utiliser le mode Test (--test-mode). Ce mode déroule le script normalement mais ne déclenche pas les photos.  
> Mode simulation : python main.py config_eclipse.txt --test-mode



# Fichier log
![Static Badge](https://img.shields.io/badge/text-under%20construction-orange)
