=======================
Spiral Abyss (深境螺旋)
=======================

The **Spiral Abyss** is a special type of `Domain`_ unlocked at `Adventure Rank`_ (冒险等级) 20 located in `Musk Reef`_,
which can be accessed through the wormhole in the sky at the edge of Cape Oath.

.. image:: ../img/Spiral_Abyss_Locked.png
    :align: center

The Spiral Abyss consists of two main parts:

1. the Abyss Corridor (Floors 1–8)
2. the Abyssal Moon Spire (Floors 9–12. Clear all 8 floors of the Abyss Corridor to permanently unlock the Abyssal Moon
   Spire.)

.. note::
    This module deals with part 2 only, which is the Abyssal Moon Spire (Floors 9 - 12)

.. _Domain: https://genshin-impact.fandom.com/wiki/Domain
.. _Adventure Rank: https://genshin-impact.fandom.com/wiki/Adventure_Rank
.. _Musk Reef: https://genshin-impact.fandom.com/wiki/Musk_Reef


Periods, Floors, and Chambers
=============================

The Spiral Abyss is divided into 12 **floors**, with each floor containing 3 **chambers**. In the Abyss Corridor, all
enemies are at the same level. In the Abyssal Moon Spire, the enemies in each chamber gradually increases in level (or
**enemy level** as we shall call instead in context of Peitho Data).

In floors where 2 teams are required, the second **half** of the chamber starts with the time remaining from the first
half.

Seemingly following the lunar cycle of another world, the Abyssal Moon Spire will reset itself twice a month, occurring
on the first and sixteenth days of the month, which may also cause a new **period** of Blessing of the Abyssal Moon to
begin


Data API
========

.. automodule:: peitho_data.genshin_impact.spiral_abyss.period_info
   :members:
   :undoc-members:


Internals
=========

.. toctree::
   :caption: Spiral Abyss Internals
   :hidden:

   spiral_abyss_internal

:doc:`spiral_abyss_internal`
    Get to know how Spiral Abyss works internally
