===============================
Spiral Abyss Analysis Internals
===============================


Period Analysis Config
======================

Information of all Spiral Abyss periods (the Abyssal Moon Spire) is obtained by analysing static HTML of
`Biligame Spiral Abyss Wiki page`_ using `BeautifulSoup`_

Each period info is **request-based**, i.e. we tell Peitho Data which period to analyze by supplying a config file of
in the following JSON schema:

.. literalinclude:: ../../../peitho_data/genshin_impact/spiral_abyss/periods.json
   :language: json
   :linenos:
   :caption: Period Config

- The value of the ``period`` field will be used as the key in the dict returned from
  :mod:`get_period_info_map <peitho_data.genshin_impact.spiral_abyss.period_info.get_period_info_map>` and, hence, can
  be arbitrary
- ``periodKey`` is the span ID of the period section. The span signifies the starting point of a period analysis. For
  example, on the `Biligame Spiral Abyss Wiki page`_, the section for Jul. ~ Aug. periods has an HTML ID shown in the
  ``span`` element on the right, if we put the ID value (``2022.E5...``) in the `periodKey`, Peitho Data will analyze
  and returns the data for Jul. ~ Aug. period from that page

  .. image:: ../img/spiral-abyss-period-key.png
      :align: center

.. _Biligame Spiral Abyss Wiki page: https://wiki.biligame.com/ys/渊月螺旋
.. _BeautifulSoup: https://www.crummy.com/software/BeautifulSoup/bs4/doc/


Getting Info by Analysing HTML
==============================

Peitho Data iterates through each of the config entries (i.e. period) in config file above, request the HTML remotely,
and parsing the HTML locally by fetching various info; each type of info is a separte function call shown in the
function call graph below:

.. callgraph:: peitho_data.genshin_impact.spiral_abyss.period_info.get_period_info_map
   :toctree: api
   :zoomable:
   :direction: horizontal


Internal API
============

.. automodule:: peitho_data.genshin_impact.spiral_abyss.period_info
   :noindex:
   :members:
   :undoc-members:
   :private-members:
   :special-members:
