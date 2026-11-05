# Lab 3 record

Name: Rishav

Roll no.: 2301730245

**1. Configuration management with Ansible**

Use Python 3.13 or newer for the current Ansible release. The demo node is an
Ubuntu container with Python installed; Ansible connects through Docker.

```bash
pip install ansible-core
ansible-galaxy collection install -r ansible/requirements.yml
docker run -d --name lab3-node -p 127.0.0.1:8081:80 ubuntu:24.04 sleep infinity
docker exec lab3-node sh -c 'apt-get update && apt-get install -y python3'
ansible-playbook -i ansible/inventory.ini ansible/playbook.yml
curl --fail http://localhost:8081/
ansible-playbook -i ansible/inventory.ini ansible/playbook.yml
```

The playbook records the student details, installs nginx and renders a page from
a template. A second run checks idempotency: unchanged files and an already
running service should not need another change.

**2. Infrastructure as code with Terraform**

Terraform uses the Docker provider, so this exercise does not need a cloud account.
Set `DOCKER_HOST` if Terraform cannot find the socket used by Docker Desktop:

```bash
export DOCKER_HOST="$(docker context inspect --format '{{.Endpoints.docker.Host}}')"
cd terraform
terraform init
terraform fmt -check
terraform validate
terraform plan
terraform apply
terraform apply -var='replicas=4'
terraform state list
terraform destroy -var='replicas=4'
cd ..
```

Each nginx container gets a different localhost port starting at 8082. Changing
`replicas` changes the declared count, and Terraform plans the corresponding
containers. State and plan files are ignored by Git.

**3. Prometheus and Grafana**

Start the monitoring stack from the README. Open `/health` and `/beta` a few times,
then check the Prometheus targets page and the provisioned Grafana dashboard.
The counter records route and HTTP status, while the histogram measures response
time. Unknown paths share one label to avoid creating a new series for each URL.
The metrics endpoint is excluded from request counts.

The demo uses one Gunicorn worker with four threads so its in-process metrics
cover all requests. More workers would need Prometheus multiprocess collection.

**4. Centralized logging**

The app writes one JSON object per request into the shared `rishav-lab3-applogs`
volume. Logstash reads the file and parses its timestamp, then sends the event
to Elasticsearch. Kibana searches the `rishav-lab3-*` indices. The Logstash read
position and Elasticsearch data both have persistent volumes.

Give Docker enough memory for the ELK stack. On Linux, check Elasticsearch's
host requirement if it refuses to start:

```bash
sudo sysctl -w vm.max_map_count=262144
docker compose -f logging/docker-compose.yml logs --tail=30
curl --fail http://localhost:9200/_cluster/health
```

**5. DevSecOps**

```bash
pip install -r security/requirements.txt
pip-audit -r app/requirements.txt
bandit -r app/ -q
docker build -f docker/Dockerfile -t devops-lab3-app:3.0.0 .
trivy image --exit-code 1 --severity HIGH,CRITICAL devops-lab3-app:3.0.0
```

Create a Jenkins Pipeline job with this repository and script path
`security/Jenkinsfile`. The agent needs Python, Docker, Trivy and the JUnit plugin.
Dependency audit and Bandit failures block later stages. Trivy also exits with a
failure for high or critical findings. Rebuild the base image and resolve scan
findings before rerunning; vulnerability results can change as databases update.

**6. Feature flags, load tests and browser tests**

```bash
docker run -d --name lab3-beta -p 127.0.0.1:5004:5000 -e FEATURE_BETA=true devops-lab3-app:3.0.0
curl --fail http://localhost:5004/beta
pip install selenium==4.53.0
python tests/selenium_check.py http://localhost:5004
ab -n 1000 -c 20 http://localhost:5004/health
```

Install Chrome for the Selenium test and ApacheBench for `ab`. Selenium checks
the health response and enabled flag, then saves a real screenshot. With the
flag off, `/beta` returns 404. With it on, the same image returns 200. The flag is
read at startup, so changing it requires recreating the container, without rebuilding.

**7. Monitoring and DevSecOps report**

Metrics help identify failures and slow requests. Logs give details about an
individual request. Ansible and Terraform keep setup repeatable, while the
security pipeline checks changes before release. Feature flags let a feature be
enabled separately from an image build. Record the test and scan results when
running each exercise.

Cleanup:

```bash
docker rm -f lab3-beta lab3-node
docker compose -f logging/docker-compose.yml down
docker compose -f monitoring/docker-compose.yml down
```
