## Configuration 🔧

Before running the scripts in the Grafana Splunk folder, make sure to configure the `config.py` file with the necessary credentials and settings.

### Update Splunk Configuration

In the `config.py` file within the Splunk folder, locate the `SPLUNK_HEC_TOKEN` variable and replace `'INSERT YOUR TOKEN HERE'` with your actual Splunk HTTP Event Collector token:

```python
# Splunk details
SPLUNK_HEC_TOKEN = 'YOUR_ACTUAL_SPLUNK_HEC_TOKEN'
```
