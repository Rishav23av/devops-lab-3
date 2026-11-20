# Lab 3 observations

Rishav | Roll no. 2301730245

- Ansible configured the Docker node and the local record. Its second run reported changed=0 on both hosts.
- Terraform created two nginx containers and then added two more when the replica count changed to four.
- Prometheus reported the app target UP, and Grafana loaded the provisioned dashboard.
- Logstash read the shared JSON log file. Kibana displayed the ingested request events.
- Jenkins build 1 failed its image gate because the Debian base had high-severity findings, including packages without available fixes.
- Switching to Alpine and updating its packages allowed build 2 to pass the same Trivy gate. The dependency audit and Bandit checks passed too.
- The beta flag returned 404 when disabled and 200 when enabled. Selenium checked the enabled instance and saved a screenshot.
- ApacheBench completed 1000 requests with no failures. These timings describe this local run, rather than a production capacity result.

See [screenshots](screenshots/README.md), [command output](commands/) and [reports](../reports/README.md).

Additional verification on 20 November 2026 checked both beta-flag states in isolated containers. Disabled returned 404 and enabled returned 200. Headless Chrome checked health and the enabled feature successfully; its output, JSON request events and dated screenshot are retained. The original load run targeted port 5003; the enabled-beta example uses port 5004.
