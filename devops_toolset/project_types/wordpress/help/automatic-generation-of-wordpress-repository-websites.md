# Automatic generation of WordPress repository websites

WordPress automated demo site.<br><br>
![Logo](../../../../.media/WordPress-logotype-simplified-site-100px.png)

# Description

This site is generated automatically:
* WordPress core files
* wp-config.php settings
* Database creation and customization
* Theme
* Plugins

After the automatic generation you customize your child theme, add your plugins and set everything as you like. That is what you commit to your repository.

# Getting started

## Step by step

1. [Install Python](https://www.python.org/downloads/) if you don't have it already in your computer.
2. Install devops-toolset package using the command ``pip install devops-toolset``
3. Place the site configuration file ``site.json`` to the root path. If you don't have this file the script will prompt you for using the default one.
4. Place your zipped theme and child-theme in the root path (you will need a custom `site.json` file for that).
5. Call the `devops_toolset.project_types.wordpress.scripts.generate_wordpress.py`. At the end of the file you can see the parameters you need to pass to the script.
6. Update `.gitignore` according to your needs.
7. Update `project.xml` to match your project values.
8. Update `README.md` file according to your needs.
