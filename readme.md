## En bref

NYTimes data est une application permettant d'analyser chaque jour les articles les plus lus de la veille, et ainsi de dégager des tendances sur le mois.

### Pipeline de données

- Une pipeline de données récupère les données depuis l'API Developer du Times.
- Un orchestrateur (Airflow) transmet ensuite ces données à un data lake sur GCP (Cloud Storage) après transformation.
- Les données transformées sont envoyées dans une data warehouse (BigQuery).
- L'infrastructure cloud est construite grâce à Terraform.
- Docker permet d'éxécuter les différents services nécessaires au fonctionnement de la pipeline.
- Data Looker permet ensuite de visualiser les données grâce à des dashboards.

### Déploiement et observabilité

- La pipeline est déployée sur une machine virtuelle Hetzner.
- La CI/CD de GitHub Actions et d'ArgoCD permettent d'automatiser la mise en production de modifications.
- K3S, une version allégée de Kubernetes est utilisé en tant que qu'orchestrateur.
- Prometheus et Grafana se chargent de l'observabilité de la machine virtuelle.
