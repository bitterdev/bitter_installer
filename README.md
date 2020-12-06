# Bitter Installer

This python script is a CLI application that allwos you to install the [Professional Website Bundle](https://www.bitter.de/shop/bundles/professional-website) and/or the [Professional Shop Bundle](https://www.bitter.de/shop/bundles/professional-shop) for concrete5. 

Furthermore this python script checks if concrete5 is already installed in the current directory and if not it downloads the latest release and install it automatically.

You can install the bitter installer on a **Ubuntu environment** by the following commands:

```
apt-get -y install dialog python3 python3-setuptools
easy_install3 pip
pip install pythondialog
pip install requests
curl –o /usr/local/bin/bitter-installer.py https://raw.githubusercontent.com/bitterdev/bitter_installer/master/bitter-installer.py
```

Then open the `~/.bash_profile` or `~/.bashrc` file and append the following line to the file:

```
alias bitter-installer='python3 /usr/local/bin/bitter-installer.py'
```

You can use `nano`, `vi` or any other text editor of your choice.

Once you have installed the bitter installer you can navigate to the webspace directory where you want to install concrete5 together with one of the bundles by executing the following command `bitter-installer`.
