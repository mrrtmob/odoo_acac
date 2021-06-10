===========
Restful API
===========

Enables a REST API for the Odoo server. The API has routes to
authenticate and retrieve a token. Afterwards, a set of routes to
interact with the server are provided.

Installation
============

To install this module, you need to:

Download the module and add it to your Odoo addons folder. Afterward, log on to
your Odoo server and go to the Apps menu. Trigger the debug mode and update the
list by clicking on the "Update Apps List" link. Now install the module by
clicking on the install button.

Another way to install this module is via the package management for Python
(`PyPI <https://pypi.org/project/pip/>`_).

To install our modules using the package manager make sure
`odoo-autodiscover <https://pypi.org/project/odoo-autodiscover/>`_ is installed
correctly. Then open a console and install the module by entering the following
command:

``pip install --extra-index-url https://nexus.openeducatit.at/repository/odoo/simple <module>``

The module name consists of the Odoo version and the module name, where
underscores are replaced by a dash.

**Module:** 

``odoo<version>-addon-<module_name>``

**Example:**

``sudo -H pip3 install --extra-index-url https://nexus.openeducatit.at/repository/odoo/simple odoo11-addon-openeducat-utils``

Once the installation has been successfully completed, the app is already in the
correct folder. Log on to your Odoo server and go to the Apps menu. Trigger the 
debug mode and update the list by clicking on the "Update Apps List" link. Now
install the module by clicking on the install button.

The biggest advantage of this variant is that you can now also update the app
using the "pip" command. To do this, enter the following command in your console:

``pip install --upgrade --extra-index-url https://nexus.openeducatit.at/repository/odoo/simple <module>``

When the process is finished, restart your server and update the application in 
Odoo. The steps are the same as for the installation only the button has changed
from "Install" to "Upgrade".

You can also view available Apps directly in our `repository <https://nexus.openeducatit.at/#browse/browse:odoo>`_
and find a more detailed installation guide on our `website <https://openeducatit.at/page/open-source>`_.

For modules licensed under OPL-1, you will receive access data when you purchase
the module. If the modules were not purchased directly from
`OpenEduCat IT <https://www.openeducatit.at/>`_ please contact our support (support@openeducatit.at)
with a confirmation of purchase to receive the corresponding access data.

Upgrade
============

To upgrade this module, you need to:

Download the module and add it to your Odoo addons folder. Restart the server
and log on to your Odoo server. Select the Apps menu and upgrade the module by
clicking on the upgrade button.

If you installed the module using the "pip" command, you can also update the
module in the same way. Just type the following command into the console:

``pip install --upgrade --extra-index-url https://nexus.openeducatit.at/repository/odoo/simple <module>``

When the process is finished, restart your server and update the application in 
Odoo, just like you would normally.

Configuration
=============

In case the module should be active in every database just change the
auto install flag to ``True``. To activate the routes even if no database
is selected the module should be loaded right at the server start. This
can be done by editing the configuration file or passing a load parameter to
the start script.

Parameter: ``--load=web,openeducat_rest``

Usage
=============

This module has no direct visible effect on the system. It provides a set of
routes to interact with the system via HTTP requests.

API Documentation
=================

**Version**
-----------

Retrieves the system version information.

-  **URL**

   */api*

-  **Method:**

   ``GET``

-  **Success Response:**

   -  **Code:** 200 **Content:** ``{...}``

**Change Master Password**
--------------------------

Changes the master password.

-  **URL**

   */api/change_master_password*

-  **Method:**

   ``POST``

-  **Data Params**

   **Required:**

   ``password_new=[alphanumeric]``

   **Optional:**

   ``password_old=[alphanumeric]``

-  **Success Response:**

   -  **Code:** 200 **Content:** ``True``

-  **Error Response:**

   -  **Code:** 400 BAD REQUEST

**Database List**
-----------------

List the available databases.

-  **URL**

   */api/database/list*

-  **Method:**

   ``GET``

-  **Success Response:**

   -  **Code:** 200 **Content:** ``{...}``

-  **Error Response:**

   -  **Code:** 400 BAD REQUEST


**Database Create**
-------------------

Creates a new database.

-  **URL**

   */api/database/create*

-  **Method:**

   ``POST``

-  **Data Params**

   **Required:**

   ``database_name=[alphanumeric]``

   ``admin_login=[alphanumeric]``

   ``admin_password=[alphanumeric]``

   **Optional:**

   ``master_password=[alphanumeric]``

   ``lang=[alphanumeric]``

   ``country_code=[alphanumeric]``

-  **Success Response:**

   -  **Code:** 200 **Content:** ``True``

-  **Error Response:**

   -  **Code:** 400 BAD REQUEST **Content:**
      ``{'error': "arguments_missing ..."}``

**Database Duplicate**
----------------------

Duplicates a database.

-  **URL**

   */api/database/duplicate*

-  **Method:**

   ``POST``

-  **Data Params**

   **Required:**

   ``database_old=[alphanumeric]``

   ``database_new=[alphanumeric]``

   **Optional:**

   ``master_password=[alphanumeric]``

-  **Success Response:**

   -  **Code:** 200 **Content:** ``True``

-  **Error Response:**

   -  **Code:** 400 BAD REQUEST **Content:**
      ``{'error': "arguments_missing ..."}``

**Database Drop**
-----------------

Drops a database.

-  **URL**

   */api/database/drop*

-  **Method:**

   ``POST``

-  **Data Params**

   **Required:**

   ``database_name=[alphanumeric]``

   **Optional:**

   ``master_password=[alphanumeric]``

-  **Success Response:**

   -  **Code:** 200 **Content:** ``True``

-  **Error Response:**

   -  **Code:** 400 BAD REQUEST **Content:**
      ``{'error': "arguments_missing ..."}``

**Database Backup**
-------------------

Creates a backup.

-  **URL**

   */api/database/backup*

-  **Method:**

   ``POST``

-  **Data Params**

   **Required:**

   ``database_name=[alphanumeric]``

   **Optional:**

   ``master_password=[alphanumeric]``

   ``backup_format=[zip|dump]``

-  **Success Response:**

   -  **Code:** 200 **Content:** ``File Response``

-  **Error Response:**

   -  **Code:** 400 BAD REQUEST **Content:**
      ``{'error': "arguments_missing ..."}``

**Database Restore**
--------------------

Creates a backup.

-  **URL**

   */api/database/restore*

-  **Method:**

   ``POST``

-  **Data Params**

   **Required:**

   ``database_name=[alphanumeric]``

   ``backup_file=[file]``

   **Optional:**

   ``master_password=[alphanumeric]``

   ``copy=[True|False]``

-  **Success Response:**

   -  **Code:** 200 **Content:** ``True``

-  **Error Response:**

   -  **Code:** 400 BAD REQUEST **Content:**
      ``{'error': "arguments_missing ..."}``

**Authentication**
------------------

Generates the API token based on the given login informations.

-  **URL**

   */api/authenticate*

-  **Method:**

   ``POST``

-  **Data Params**

   **Required:**

   ``db=[alphanumeric]``

   ``login=[alphanumeric]``

   ``password=[alphanumeric]``

-  **Success Response:**

   -  **Code:** 200 **Content:**
      ``{token: "dbULH4OKKEp.......Kby-KE4OKEpK2M"}``

-  **Error Response:**

   -  **Code:** 404 NOT FOUND **Content:** ``{"error": "invalid_db"}``

   -  **Code:** 500 INTERNAL SERVER ERROR **Content:**
      ``{"error": "rest_api_not_supported"}``

   -  **Code:** 401 UNAUTHORIZED **Content:**
      ``{"error": "invalid_login"}``

   -  **Code:** 400 BAD REQUEST **Content:**
      ``{'error': "arguments_missing ..."}``

**Life**
--------

Returns the remaining lifetime to a given token.

-  **URL**

   */api/life*

-  **Method:**

   ``GET``

-  **URL Params**

   **Required:**

   ``token=[alphanumeric]``

   **Optional:**

   ``db=[alphanumeric]``

-  **Success Response:**

   -  **Code:** 200 **Content:** ``3559``

-  **Error Response:**

   -  **Code:** 403 FORBIDDEN **Content:** ``"error": "token_invalid"``

   -  **Code:** 400 BAD REQUEST **Content:**
      ``{'error': "arguments_missing ..."}``

**Refresh**
-----------

Refreshes the token lifetime.

-  **URL**

   */api/refresh*

-  **Method:**

   ``POST``

-  **Data Params**

   **Required:**

   ``token=[alphanumeric]``

   **Optional:**

   ``db=[alphanumeric]``

-  **Success Response:**

   -  **Code:** 200 **Content:** ``True``

-  **Error Response:**

   -  **Code:** 403 FORBIDDEN **Content:** ``"error": "token_invalid"``

   -  **Code:** 400 BAD REQUEST **Content:**
      ``{'error': "arguments_missing ..."}``

**Close**
---------

Closes the API connection.

-  **URL**

   */api/close*

-  **Method:**

   ``POST``

-  **Data Params**

   **Required:**

   ``token=[alphanumeric]``

   **Optional:**

   ``db=[alphanumeric]``

-  **Success Response:**

   -  **Code:** 200 **Content:** ``True``

-  **Error Response:**

   -  **Code:** 403 FORBIDDEN **Content:** ``"error": "token_invalid"``

   -  **Code:** 400 BAD REQUEST **Content:**
      ``{'error': "arguments_missing ..."}``

**Search**
----------

Returns the search result.

-  **URL**

   */api/search*

-  **Method:**

   ``GET``

-  **URL Params**

   **Required:**

   ``token=[alphanumeric]``

   **Optional:**

   ``db=[alphanumeric]``

   ``id=[integer]``

   ``model=[alphanumeric]``

   ``domain=[json]``

   ``context=[json]``

   ``count=[bool]``

   ``limit=[integer]``

   ``offset=[integer]``

   ``order=[alphanumeric]``

-  **Success Response:**

   -  **Code:** 200 **Content:** ``{...}``

-  **Error Response:**

   -  **Code:** 403 FORBIDDEN **Content:** ``"error": "token_invalid"``

   -  **Code:** 400 BAD REQUEST **Content:**
      ``{'error': "arguments_missing ..."}``
      
**Read**
--------

Returns the search result of the given fields.

-  **URL**

   */api/read*

-  **Method:**

   ``GET``

-  **URL Params**

   **Required:**

   ``token=[alphanumeric]``

   **Optional:**

   ``db=[alphanumeric]``

   ``id=[integer]``

   ``fields=[json]``

   ``model=[alphanumeric]``

   ``domain=[json]``

   ``context=[json]``

   ``count=[bool]``

   ``limit=[integer]``

   ``offset=[integer]``

   ``order=[alphanumeric]``

-  **Success Response:**

   -  **Code:** 200 **Content:** ``{...}``

-  **Error Response:**

   -  **Code:** 403 FORBIDDEN **Content:** ``"error": "token_invalid"``

   -  **Code:** 400 BAD REQUEST **Content:**
      ``{'error': "arguments_missing ..."}``
      
**Create**
----------

Creates a new record.

-  **URL**

   */api/create*

-  **Method:**

   ``POST``

-  **Data Params**

   **Required:**

   ``token=[alphanumeric]``

   **Optional:**

   ``model=[alphanumeric]``

   ``values=[json]``

   ``context=[json]``

-  **Success Response:**

   -  **Code:** 200 **Content:** ``{...}``

-  **Error Response:**

   -  **Code:** 403 FORBIDDEN **Content:** ``"error": "token_invalid"``

   -  **Code:** 400 BAD REQUEST **Content:**
      ``{'error': "arguments_missing ..."}``
      
**Write**
---------

Updates an existing record.

-  **URL**

   */api/write*

-  **Method:**

   ``PUT``

-  **Data Params**

   **Required:**

   ``token=[alphanumeric]``

   ``ids=[json]``

   **Optional:**

   ``model=[alphanumeric]``

   ``values=[json]``

   ``context=[json]``

-  **Success Response:**

   -  **Code:** 200 **Content:** ``True``

-  **Error Response:**

   -  **Code:** 403 FORBIDDEN **Content:** ``"error": "token_invalid"``

   -  **Code:** 400 BAD REQUEST **Content:**
      ``{'error': "arguments_missing ..."}``
      
**Unlink**
----------

Deletes an existing record.

-  **URL**

   */api/unlink*

-  **Method:**

   ``DELETE``

-  **Data Params**

   **Required:**

   ``token=[alphanumeric]``

   ``ids=[json]``

   **Optional:**

   ``model=[alphanumeric]``

   ``context=[json]``

-  **Success Response:**

   -  **Code:** 200 **Content:** ``True``

-  **Error Response:**

   -  **Code:** 403 FORBIDDEN **Content:** ``"error": "token_invalid"``

   -  **Code:** 400 BAD REQUEST **Content:**
      ``{'error': "arguments_missing ..."}``

**Call**
--------

Generic method call.

-  **URL**

   */api/call*

-  **Method:**

   ``POST``

-  **Data Params**

   **Required:**

   ``token=[alphanumeric]``

   ``method=[alphanumeric]``

   **Optional:**

   ``ids=[json]``

   ``context=[json]``

   ``args=[json]``

   ``kwargs=[json]``

-  **Success Response:**

   -  **Code:** 200 **Content:** ``{...}``

-  **Error Response:**

   -  **Code:** 403 FORBIDDEN **Content:** ``"error": "token_invalid"``

   -  **Code:** 400 BAD REQUEST **Content:**
      ``{'error': "arguments_missing ..."}``
      
**Report**
----------

Generate reports.

-  **URL**

   */api/report*

-  **Method:**

   ``GET``

-  **Data Params**

   **Required:**

   ``token=[alphanumeric]``

   ``report=[alphanumeric]``

   ``ids=[json]``

   **Optional:**

   ``type=[html|pdf]``

   ``context=[json]``

   ``args=[json]``

   ``kwargs=[json]``

-  **Success Response:**

   -  **Code:** 200 **Content:** ``file``

-  **Error Response:**

   -  **Code:** 403 FORBIDDEN **Content:** ``"error": "token_invalid"``

   -  **Code:** 400 BAD REQUEST **Content:**
      ``{'error': "arguments_missing ..."}``
      
**Binary**
----------

Downloads a binary file.

-  **URL**

   */api/binary*

-  **Method:**

   ``GET``

-  **Data Params**

   **Required:**

   ``token=[alphanumeric]``

   **Optional:**

   ``xmlid=[alphanumeric]``

   ``model=[alphanumeric]``

   ``id=[number]``

   ``field=[alphanumeric]``

   ``filename=[alphanumeric]``

   ``filename_field=[alphanumeric]``

   ``unique=[alphanumeric]``

   ``mimetype=[alphanumeric]``

   ``data=[data]``

-  **Success Response:**

   -  **Code:** 200 **Content:** ``file``

-  **Error Response:**

   -  **Code:** 403 FORBIDDEN **Content:** ``"error": "token_invalid"``

   -  **Code:** 400 BAD REQUEST **Content:**
      ``{'error': "arguments_missing ..."}``

Credits
=======

Contributors
------------

* Mathias Markl <mathias.markl@openeducatit.at>

Images
------------

Some pictures are based on or inspired by:

* `Prosymbols <https://www.flaticon.com/authors/prosymbols>`_
* `Smashicons <https://www.flaticon.com/authors/smashicons>`_

Author & Maintainer
-------------------

This module is maintained by the `OpenEduCat <https://www.openeducatit.at/>`_.

OpenEduCat IT is an Austrian company specialized in customizing and extending Odoo.
We develop custom solutions for your individual needs to help you focus on
your strength and expertise to grow your business.

If you want to get in touch please contact us via mail
(sale@openeducatit.at) or visit our website (https://openeducatit.at).
