# leakMonitor
Monitors leaked data. Framework to be built on.
### Outline

The app has a script that should run daily to search for potential credential leaks. At the moment Github and Google searches are included. Don't expect much on the code, it's very basic, especially the PHP. The folder structure is outlined below:

![image](https://user-images.githubusercontent.com/954507/126834412-6862c526-28d2-4194-90c6-ef1f7d7c98b2.png)


```jsx

> db -- hosts the database
> script -- monitor script is stored here
> web -- web frontend
```

**Setup**

To setup the script you must have apache2 installed with PHP for the front end to work, the below assumes this has already been set up. 

*Let's get it onto our system*

```bash
cd ~
git clone XXXXX
cd leakMonitor
python3 -m pip install requests beautifulsoup4 colorama
```

*Set up the script to run daily at 2am*

```bash
nano /etc/cron.daily/monitor

#!/bin/bash
python3 ~/leakmonitor/script/monitor.py ~/cron.log 2>&1

test -x /usr/sbin/anacron || { cd / && run-parts --report /etc/cron.daily; }
```

*Set up the web frontend, change folders as required*

```bash
sudo ln -sT ~/leakmonitor/web /var/www/leakmonitor
sudo chgrp www-data ~ ~/leakmonitor/
sudo chgrp www-data ~/leakmonitor/web
chmod 710 ~ ~/leakmonitor/
sudo chmod -R 755 /var/www/
```

*Let's configure the script now, example configuration is given below*

```bash
{
    "Github":[{
    "enabled": true,
    "gitfilenames":[ 
        "app.config",
        "application.properties",
        "appSettings.config",
        "settings.json",
        "web.config"],
    "gitwords":"password",
    "domains": ".com,
    "gitauth": "ghp_XXXXXXXM5ZhK",
    "gitpages": "3"
    }    
    ],
    "Google":[{
        "enabled": true,
        "sitesinurl":[ 
            "anonfiles.com",
        "throwbin.io"],
        "domains": [
            ".com",
            ".org"],
        "googlekey": "",
        "googleresults": "250",
        "googlepages": "1"
        }    
        ]                                      
}
```
**ToDo**

- [ ]  Settings editor in front end
- [ ]  Multiple domain searches on GitHub
- [ ]  Document template for new sites
