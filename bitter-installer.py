# Bitter Installer
#
# Copyright 2020 Fabian Bitter
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

import locale
import time
import os
import subprocess
import re
import stat
import shutil
import zipfile
import requests
from distutils.version import LooseVersion, StrictVersion
from dialog import Dialog

base_dir = os.path.dirname(os.path.abspath(__file__))
concrete_interpreter = base_dir + "/concrete/bin/concrete5"

locale.setlocale(locale.LC_ALL, '')

d = Dialog(dialog="dialog")

d.set_background_title("Bitter Software Installer")

def shell_exec(command):
	p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

	exit_code = 1

	try:
		(output, err) = p.communicate(timeout=300)

		exit_code = p.wait()

		return (exit_code, output)
	except subprocess.TimeoutExpired:
		proc.terminate()

		return (exit_code, "")

def is_concrete_available():
	return os.path.exists(concrete_interpreter)

def is_concrete_compatible():
	(exit_code, output) = shell_exec(concrete_interpreter + " c5:info")

	if (exit_code == 0):
		result = re.search('Core Version - (.*)\n', output.decode('utf-8'))

		concrete_version = result.group(1).strip()

		return StrictVersion(concrete_version) >= StrictVersion("8.3.0")
	else:
		return False

def install_concrete():
	if d.yesno("You have to install concrete5 before you can continue. Do you want to install concrete5 now?") == d.OK:

		code, username = d.inputbox("Please enter the site name.", init='Test Environment')

		if (code != d.OK):
			return False

		code, admin_email = d.inputbox("Please enter the admin email.", init='admin')

		if (code != d.OK):
			return False

		code, admin_password = d.passwordbox("Please enter the admin password.", init='admin', insecure=True)

		if (code != d.OK):
			return False

		code, db_server = d.inputbox("Please enter the database server.", init='127.0.0.1')

		if (code != d.OK):
			return False

		code, db_database = d.inputbox("Please enter the database name.", init='concrete5')

		if (code != d.OK):
			return False

		code, db_username = d.inputbox("Please enter the database username.", init='root')

		if (code != d.OK):
			return False

		code, db_password = d.passwordbox("Please enter the database password.", init='root', insecure=True)

		if (code != d.OK):
			return False

		d.gauge_start()

		d.gauge_update(15, "Installing concrete5...", update_text=1)

		(exit_code, output) = shell_exec("%s c5:install --allow-as-root --db-server=\"%s\" --db-username=\"%s\" --db-password=\"%s\" --db-database=\"%s\" --admin-email=\"%s\" --admin-password=\"%s\" --starting-point=elemental_blank" % (concrete_interpreter, db_server, db_username, db_password, db_database, admin_email, admin_password))

		d.gauge_stop()

		if (exit_code == 0):
			return True
		else:
			d.msgbox("There was an error while installing concrete5.")
			return False

	else:
		d.msgbox("You have to install concrete5 before you can continue.")
		return False

def is_concrete_installed():
	(exit_code, output) = shell_exec(concrete_interpreter + " c5:is-installed")

	if (output.decode('utf-8').strip() == "concrete5 is installed"):
		return True
	else:
		return False

def is_marketplace_cli_installed():
	return os.path.exists(base_dir + "/packages/marketplace_cli")

def install_marketplace_cli():
	# download marketplace_cli
	download_file("https://github.com/bitterdev/marketplace_cli/releases/download/1.0/marketplace_cli.zip", base_dir + "/marketplace_cli.zip")

	# unzip marketplace_cli
	zip_ref = zipfile.ZipFile(base_dir + "/marketplace_cli.zip", 'r')
	zip_ref.extractall(base_dir + "/packages")
	zip_ref.close()

	# remove temp file
	os.remove(base_dir + "/marketplace_cli.zip")

	# install
	(success, error_message) = install_package("marketplace_cli", "")
	return success

def change_permissions_recursive(path, mode):
	for root, dirs, files in os.walk(path, topdown=False):
		for dir in [os.path.join(root,d) for d in dirs]:
			os.chmod(dir, mode)
	for file in [os.path.join(root, f) for f in files]:
		os.chmod(file, mode)

def download_file(url, file):
	response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
	out_file = open(file, 'wb')
	out_file.write(response.content)

def download_concrete():
	if d.yesno("You have to download concrete5 before you can continue. Do you want to download concrete5 now?") == d.OK:

		d.gauge_start()

		# download concrete5
		d.gauge_update(0, "Downloading concrete5...", update_text=1)
		download_file("https://www.concrete5.org/download_file/-/view/113632/", base_dir + "/concrete5.zip")

		# unzip concrete5
		d.gauge_update(50, "Extracting concrete5...", update_text=1)
		zip_ref = zipfile.ZipFile(base_dir + "/concrete5.zip", 'r')
		zip_ref.extractall(base_dir + "/")
		zip_ref.close()

		# move files
		d.gauge_update(75, "Move concrete5 files...", update_text=1)
		source = os.listdir(base_dir + "/concrete5-8.4.4/")
		for files in source:
			shutil.move(base_dir + "/concrete5-8.5.4/" + files, base_dir + "/")

		# remove temp file
		d.gauge_update(90, "Cleanup...", update_text=1)

		os.remove(base_dir + "/concrete5.zip")
		shutil.rmtree(base_dir + "/concrete5-8.5.4")

		# make c5 interpreter executable
		d.gauge_update(95, "Set permissions...", update_text=1)

		st = os.stat(concrete_interpreter)
		os.chmod(concrete_interpreter, st.st_mode | stat.S_IEXEC)

		# chmod 777
		change_permissions_recursive(base_dir + "/application/files", 0o0777)
		change_permissions_recursive(base_dir + "/application/config", 0o0777)
		change_permissions_recursive(base_dir + "/application/languages", 0o0777)
		change_permissions_recursive(base_dir + "/packages", 0o0777)
		change_permissions_recursive(base_dir + "/updates", 0o0777)

		d.gauge_stop()

		return True

	else:
		d.msgbox("You need to execute this script in the root directory of your concrete5 project.")
		return False

def check_dependencies():
	if (is_concrete_available() == False):
		if download_concrete() == False:
			return False
	pass

	if (is_concrete_compatible() == False):
		d.msgbox("You need at least concrete5 version 8.3.")
		return False
	pass

	if (is_concrete_installed() == False):
		if install_concrete() == False:
			return False
	pass

	if (is_marketplace_cli_installed() == False):
		if (install_marketplace_cli() == False):
			d.msgbox("Error while installing the Marketplace CLI.")
			return False
	pass

	return True

def confirm_licenses_purchased(purchase_url):
	if d.yesno("Do you have purchased all necessary licenses?") == d.OK:
		return True
	else:
	    d.msgbox("Please visit the %s and purchase all required licenses before continue. When your done press OK." % (purchase_url))
	    return True


def has_canonical_url():
	if d.yesno("Do you want to set a canonical URL?") == d.OK:
		code, canonical_url = d.inputbox("Please define a canonical URL.", init='http://localhost')

		if (code == d.OK):
			(success, error_message) = change_canonical_url(canonical_url)

			if (success == False):
				d.msgbox(error_message)
				return False
			else:
				return True
		else:
			return False
	else:
		return True

def get_package_list():
	code, option = d.radiolist(
		"Please select the software package you want to install.",
		choices = [
			("1", "Professional Website Bundle", True),
			("2", "Professional Shop Bundle", False)
		],
		title="Select package"
	)

	package_list = [
		"image_carousel",
		"portfolio_grid",
		"progressbar",
		"accordion_pro",
		"app_icon",
		"counter_up",
		"glossary_list",
		"smart_banner",
		"responsive_image",
		"panorama_viewer",
		"bitter_theme"
	];

	if code == d.OK:
		if option == "2":
			package_list += [
				"pdf_designer",
				"bitter_shop_system"
			]

			confirm_licenses_purchased("https://www.bitter.de/shop/bundles/professional-shop")
			pass
		else:
			confirm_licenses_purchased("https://www.bitter.de/shop/bundles/professional-website")
			pass

		return package_list
	else:
		return False
	pass

def request_credetials():
	code, username = d.inputbox("Please enter your concrete5.org username.")

	if (code == d.OK):
		code, password = d.passwordbox("Please enter your concrete5.org password.", insecure=True)

		if (code == d.OK):
			return [
				username,
				password
			]
		pass

	return False

def change_canonical_url(url):
	(exit_code, output) = shell_exec(concrete_interpreter + " marketplace:change-canonical-url \"" + url + "\"")

	if (exit_code != 0):
		return (False, get_error_message(exit_code, ""))
	else:
		return (True, None)

def download_package(package_handle, username, password):
	(exit_code, output) = shell_exec(concrete_interpreter + " marketplace:download " + package_handle + " \"" + username + "\" \"" + password + "\"")

	change_permissions_recursive(base_dir + "/packages/" + package_handle, 0o0777)

	if (exit_code != 0):
		return (False, get_error_message(exit_code, package_handle))
	else:
		return (True, None)

	return exit_code

def install_package(package_handle, arguments):
	(exit_code, output) = shell_exec(concrete_interpreter + " c5:package-install " + package_handle + " " + arguments)

	if (exit_code != 0):
		return (False, get_error_message(7, package_handle))
	else:
		return (True, None)

def download_and_install_package(package_handle, username, password):
	(success, error_message) = download_package(package_handle, username, password)

	if (success):
		if (package_handle == "bitter_theme"):
			os.chmod(base_dir + "/packages/bitter_theme/content.xml", 0o0777)
			return install_package("bitter_theme", "--full-content-swap")
		elif (package_handle == "bitter_shop_system"):
			return install_package("bitter_shop_system", "arr[]=installSampleData")
		else:
			return install_package(package_handle, "")
	else:
		return (success, error_message)


def get_error_message(exit_code, package_handle):
	if (exit_code == 1):
		return "Invalid concrete5 credentials."
	elif (exit_code == 2):
		return "The site can not connected with the marketplace."
	elif (exit_code == 3):
		return "No free license available for the package %s. Please purchase the add-on." % (package_handle)
	elif (exit_code == 4):
		return "Error while downloading the package %s." % (package_handle)
	elif (exit_code == 5):
		return "You don't have the permissions to install packages."
	elif (exit_code == 6):
		return "You don't have setted up an canonical URL."
	elif (exit_code == 7):
		return "There was an error while installing the package %s." % (package_handle)
	else:
		return "Unknown error while installing the package %s." % (package_handle)

def main():
	if check_dependencies() == True:
		if (has_canonical_url() == True):
			package_list = get_package_list()

			if package_list != False:
				total_packages = len(package_list)

				credentials = request_credetials()

				if (credentials != False):
					username = credentials[0]
					password = credentials[1]

					d.gauge_start()

					index = 0

					for package_handle in package_list:
						index += 1

						d.gauge_update(int(100 * index / total_packages), "Installing %s..." % (package_handle), update_text=1)

						(success, error_message) = download_and_install_package(package_handle, username, password)

						if (success == False):
							d.msgbox(error_message)
							break

					d.gauge_stop()

main()
