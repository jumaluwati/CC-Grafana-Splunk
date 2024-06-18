
# Cisco Catalyst Center Integration with Grafana & Splunk 🌐

This project simplifies network management by aggregating critical data from Cisco Catalyst Center and presenting it in intuitive, easy-to-digest dashboards on Grafana and Splunk. Designed for network administrators and IT professionals, this integration centralizes health scores, client statistics, issue tracking, and license consumption metrics into a single pane of glass. By consolidating this information, users can quickly assess the state of their network, identify and troubleshoot issues, and ensure optimal performance and compliance with licensing requirements.

## Main Features 🌟

- **Unified Health Scores**: View comprehensive health scores for network devices and clients in one place.
- **Real-Time Issue Tracking**: Stay ahead of network problems with a live feed of issues detected by Catalyst Center, all categorized and prioritized for efficient management.
- **License Utilization**: Monitor your license usage with detailed reports on entitlements versus deployment.
- **One-Click Insights**: Access all your key network metrics through Grafana or Splunk dashboards with a single click, saving time and simplifying your workflow.
- **Dockerized Environment**: Leverage the power of Docker to spin up your monitoring environment with ease, ensuring consistency across different systems and deployments.

## Value Proposition 💡

With this integration, you no longer need to navigate through multiple Catalyst Center dashboards to gather essential information. This solution streamlines your monitoring process, enhances visibility into network health, and empowers you to make data-driven decisions swiftly. Whether you're troubleshooting a specific client issue or conducting a broad network performance review, these dashboards are tailored to provide the insights you need in a centralized, user-friendly format.

## Prerequisites 📋

Before you begin, ensure you have met the following requirements:

- **Docker**: You have installed the latest version of [Docker](https://www.docker.com/get-started). Docker is used to create, manage, and run the containers for the services your project relies on.
- **Git**: You have installed [Git](https://git-scm.com/downloads) on your machine to clone the repository.
- **Python**: You have Python installed on your machine to run the scripts. The project is compatible with Python 3.x.
- **Network Knowledge**: You have a basic understanding of network management and monitoring concepts, which will help you make the most of the dashboards and data provided by the project.
- **Cisco Catalyst Center**: Familiarity with Cisco Catalyst Center APIs is beneficial, as the project interacts with these APIs to retrieve network data.
- **Database Knowledge**: Basic knowledge of MySQL and database operations is recommended, as the project involves pushing data to a MySQL database.
- **Grafana & Splunk**: Familiarity with Grafana and Splunk platforms is recommended for customizing and interpreting the dashboards.

No specific operating system is required as long as it can run Docker, which is available for Windows, Linux, and macOS. However, the commands provided in the documentation are for Unix-like systems and may need to be adjusted for use in Windows.


## Installation 🛠️

Steps to install your project:

1. Clone the repository:
   ```bash
   git clone https://github.com/jumaluwati/CC-Grafana-Splunk.git
   ```
2. Navigate to the project directory:
   ```bash
   cd CC-Grafana-Splunk
   ```
3. Start the services using Docker Compose:
   ```bash
   docker-compose up -d
   ```



## onfiguration & Usage  🔧

After successfully installing the project using Docker, follow these steps to get your dashboards up and running:

### Verify Docker Containers

1. Check if all Docker containers are running smoothly:
   ```bash
   docker ps
   ```
You should see all containers listed as running.
 
### Set Up phpMyAdmin
 
1. Open phpMyAdmin in your web browser by navigating to http://localhost:8080.
2. Log in with root/cisco as username and password, to manage your MySQL database.
 
### Initialize Grafana Data
 
1. Navigate to the Grafana folder in your project directory and run the Python scripts to populate your MySQL database:
   ```bash
   python3 mysql_clients_page.py
   python3 mysql_network_health.py
   python3 mysql_issues_events.py
   python3 mysql_license_overview.py
   ```
2. Verify that the data has been populated in phpMyAdmin. You should see new tables created with data in them.

### Configure Grafana
 
1. Access Grafana by visiting http://localhost:3000 in your web browser.
2. Log in with the default credentials (username: admin, password: admin) or the credentials you have set.
3. Add a new data source by selecting MySQL.
4. Fill in the details as follows:
    Host: mysql_container:3306
    Database: cc_db
    User: root
    Password: cisco
5. Test the connection and save it.


### Import Grafana Dashboard
 
1. Import the dashboard JSON file by navigating to the "+" icon on the left sidebar and selecting "Import".
2. Upload the JSON file from the Grafana folder on GitHub or paste the JSON content directly into the text field.
3. After importing, you may need to select the correct data source for each panel if it's not automatically mapped.
 
### Set Up Splunk
 
1. Wait for the Splunk container to be fully ready, which may take a couple of minutes.
2. Access the Splunk web interface at http://localhost:8000.
3. Log in with the username admin and the password you specified in the Docker Compose file.
 
### Configure Splunk Data Inputs
 
1. Add a new data source by configuring the HTTP Event Collector (HEC) in Splunk.
2. Create four indexes corresponding to your datasets: cc_network, cc_client, cc_license, cc_issues. These should match the indexes specified in your Python scripts for Splunk.
3. Set the data type to _json.
 
### Import Splunk Dashboard
 
1. Create a new dashboard in Splunk and click on "Source" to edit the XML directly.
2. Paste the XML content from the Splunk folder on GitHub into the source editor and save it.


### Run Splunk Scripts
 
1. Execute the Python scripts in the Splunk folder to start sending data to Splunk:
   ```bash
   python3 splunk_client.py
   python3 splunk_network.py
   python3 splunk_issues.py
   python3 splunk_license.py
   ```
2. Once the scripts are running, you should see the data reflected on your Splunk dashboard.
 
By following these steps, you should have fully functional Grafana and Splunk dashboards displaying your network data. If you encounter any issues, check the logs for each container, and ensure that all configurations match the details specified in your Docker Compose file and scripts.

### Note

Please note that for the Grafana dashboard, the JSON file typically includes the layout and settings for the dashboard panels but does not include the data source configuration. You will need to ensure that the data source is correctly set up in Grafana and mapped to the panels in the dashboard after importing the JSON file.

For the Splunk dashboard, the XML file should include the layout and visualizations, but you will need to ensure that the data inputs are correctly configured and that the indexes match those specified in your Python scripts.

Remember to replace any placeholder text with the actual commands and filenames used in your project.




## Dashboard View 🎆
 
### Grafana Dashboard
 
Here's what the Grafana dashboard looks like:
 
Grafana Dashboard
 
### Splunk Dashboard
 
Here's what the Splunk dashboard looks like:
 
Splunk Dashboard


 
 
## License 📝
 
This project is licensed under the MIT License - see the LICENSE file for details.
 
Contact 📬
 
Juma Luwati - jalluwar@cisco.com
 
Project Link: [https://github.com/jumaluwati/CC-Grafana-Splunk]
 


