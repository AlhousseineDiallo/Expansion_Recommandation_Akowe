import re

# Lire le fichier
with open('README.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Remplacement 1 : Normalisation min-max
content = content.replace(
    '$$\\text{X\\_normalized} = \\frac{X - X_{min}}{X_{max} - X_{min}}$$',
    '```\nX_normalized = (X - X_min) / (X_max - X_min)\n```'
)

# Remplacement 2 : Scale Score
content = content.replace(
    '$$\\text{Scale\\_Score} = \\text{TAM\\_normalized}$$',
    '```\nScale_Score = TAM_normalized\n```'
)

# Remplacement 3 : Momentum
content = content.replace(
    '$$\\text{Momentum} = 0.50 \\times \\text{lower\\_secondary\\_completion} + 0.20 \\times \\text{population\\_growth} + 0.30 \\times \\text{tertiary\\_enrollment\\_trend}$$',
    '```\nMomentum = 0.50 × lower_secondary_completion + 0.20 × population_growth + 0.30 × tertiary_enrollment_trend\n```'
)

# Remplacement 4 : AbilityToPay
content = content.replace(
    '$$\\text{AbilityToPay} = 0.60 \\times \\text{gni\\_per\\_capita\\_normalized} + 0.25 \\times \\text{education\\_exp\\_gov} + 0.15 \\times \\text{gdp\\_per\\_capita}$$',
    '```\nAbilityToPay = 0.60 × gni_per_capita_normalized + 0.25 × education_exp_gov + 0.15 × gdp_per_capita\n```'
)

# Remplacement 5 : DigitalReadiness
content = content.replace(
    '$$\\text{DigitalReadiness} = 0.40 \\times \\text{internet\\_access} + 0.60 \\times \\text{electricity\\_access}$$',
    '```\nDigitalReadiness = 0.40 × internet_access + 0.60 × electricity_access\n```'
)

# Remplacement 6 : MAS composite
content = content.replace(
    '$$\\text{MAS} = 35 \\times \\text{Scale} + 25 \\times \\text{Momentum} + 25 \\times \\text{AbilityToPay} + 15 \\times \\text{DigitalReadiness}$$',
    '```\nMAS = 35 × Scale + 25 × Momentum + 25 × AbilityToPay + 15 × DigitalReadiness\n```'
)

# Écrire le fichier modifié
with open('README.md', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Modifications appliquées avec succès!")
print("✓ Les 6 équations LaTeX ont été remplacées par des code-blocks")
