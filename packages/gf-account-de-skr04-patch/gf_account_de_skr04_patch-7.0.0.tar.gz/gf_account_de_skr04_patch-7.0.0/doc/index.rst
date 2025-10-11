#############################
Account De SKR04 Patch Module
#############################

.. to remove, see https://www.tryton.org/develop/guidelines/documentation#index.rst

.. This file is part of gf_mds_account_de_skr04_patch
   Licensed under the GNU Free Documentation License v1.3 or any later version.
   The COPYRIGHT file at the top level of this repository contains the
   full copyright notices and license terms.
   SPDX-License-Identifier: GFDL-1.3-or-later

account_de_skr04_patch
----------------------

Documentation in German, module handles specific German taxation and accounting rules for the SKR04 account plan.

Ergänzung des Moduls ``mds_account_de_skr04``:

* Berücksichtigung der Unterscheidung Ware/Dienstleistung bei der Umsatzsteuer
* Hierarchische Struktur der Umsatzsteuer, sodass Steuersatzänderungen durch Setzen der Gültigkeiten
  der jeweiligen Steuer umgesetzt werden können
* Ergänzung fehlender Umsatzsteuertatbestände
* Ergänzung fehlender Konten
* Vereinfachung der Steuerkennzifferntabelle und Anpassung an das aktuelle ELSTER-Formular
* Integration von Steuerregeln

Berücksichtigte Szenarien
-------------------------

* Ein- und Verkauf von Waren und Dienstleistungen (sonstigen Leistungen) innerhalb von Deutschland,
  in die EU und in Drittländer
* voller, ermäßigter und USt-freier Umsatzsteuersatz
* Import von Waren aus Drittländern über einen Zolldienstleister
* Kleinunternehmerregelung nach § 19 UStG
* Reverse Charge im Inland

U. a. nicht berücksichtigte Szenarien
-------------------------------------

* Selbstimport von Waren mit eigener Zollnummer
* Export in EU-Länder an Endverbraucher mit Jahresumsatz größer als OSS-Schwelle pro Kunde (OSS-Verfahren);
  das kann über das Modul ``trytond_account_tax_rule_country`` geregelt werden
* grenzüberschreitender Handel mit steuerlich individuell zu behandelnden Waren, wie Gold
* …

Umstellung vom bisherigen SKR04
-------------------------------

Durch die Installation des Moduls wird der Kontenplan SKR04 aktualisiert. Dabei werden keine bestehenden
Konten gelöscht, sondern nur neue Konten hinzugefügt. Es werden alle bestehenden Steuern als deprecated
markiert. Diese können dann durch die neuen Steuern ersetzt werden. Es ist möglich, trotz der Installation
mit den alten Steuern weiterzuarbeiten. Allerdings wird dann die Umsatzsteuererklärung nicht korrekt erstellt.

0. Planung

   * Empfehlung: Umstellung zum Stichtag (zum Beispiel Ende des Rechnungsjahres)
   * Prüfen: Soll bei dieser Gelegenheit die Aufwands- und Ertragskonten geändert werden?

1. Patch installieren

2. Tryton-Menü: „Kontenplan von Vorlage aktualisieren“

3. Gegebenenfalls neue Artikelkategorien anlegen

4. „Alte“ Umsatzsteuern durch neue ersetzen

Autoren
-------

* Jakob Fischer – Grünfischer Consulting (Programmierung)
* Wolf Drechsel – Komponentenkontor Berlin GmbH (Dokumentation)
