# MySQL Workbench Plugin
# <description>
# Written in MySQL Workbench 6.3.4

from wb import *
import grt
import mforms
import re
import string

# - Added summary (anchors links)
# - Added fonction "return to tables list"
# - Added navigation bar (anchors links)
# - Added fonction escaping underscore in markdown

ModuleInfo = DefineModule("ModelDocumentation", author="Hieu Le", version="1.0.0", description="Generate Markdown documentation from a model")

# This plugin takes no arguments
@ModuleInfo.plugin("info.hieule.wb.documentation", caption="Generate documentation (Markdown)", description="description", input=[wbinputs.currentDiagram()], pluginMenu="Utilities")
@ModuleInfo.export(grt.INT, grt.classes.db_Catalog)
def documentation(diagram):
    # ADDED : Logo
    text = "<img src=\"images/nom_logo.png\" width=\"70\" height=\"70\" align=\"right\">\n"
    text += "# Schema documentation\n\n**Database :**\n\nnom_base\n\n"
    text += "\n\n";
    # ADDED : navigation bar
    bar_nav = "".join(["<a href=\"#{}\">{} | </a>".format(x[0], x.upper()) for x in string.ascii_lowercase])
    text +=  "**<p id=\"summary\">Tables list :** </p>{} \n\n".format(bar_nav)

    # ADDED : An empty list to build-up our next summary
    list_tables = []
    
    for figure in diagram.figures:
        if hasattr(figure, "table") and figure.table:
            # Adding tables in our empty list
            list_tables.append(figure.table)

    # Build the summary
    for x in list_tables:
    # Some tables are written with double underscores...so...
    	if "__" in x.name:
    		one_tab = x.name
            # Trick : split et join => escaping underscore in markdown...
    		split_tab = one_tab.split("__")
    		escaped_tab = "\\__".join(split_tab)
    		text += " - " + "<a href=\"#{}\">".format(escaped_tab) + escaped_tab + "</a>\n\n"
    	else:
    		text += " - " + "<a href=\"#{}\">".format(x.name) + x.name + "</a>\n\n"        	

    # Write the documentation 
    for figure in diagram.figures:
        if hasattr(figure, "table") and figure.table:
            text += writeTableDoc(figure.table)

    mforms.Utilities.set_clipboard_text(text)
    mforms.App.get().set_status_text("Documentation generated into the clipboard. Paste it to your editor.")

    print "Documentation is copied to the clipboard."
    return 0


def writeTableDoc(table):
    # Wrap up anchors links for every table
    # Trick round II !
    # Bind the navigation bar anchor
    first_letter_tab = table.name
    if first_letter_tab[0] in string.ascii_uppercase:
    	bind_nav = "<span id=\"\">"
    elif first_letter_tab[0] in string.ascii_lowercase:
    	bind_nav = "<span id=\"{}\">".format(first_letter_tab[0])

    if "__" in table.name:
    	one_tab = table.name
    	split_tab = one_tab.split("__")
    	escaped_tab = "\\__".join(split_tab)
    	text = "## <p id=\"{}\">{}Table: `".format(escaped_tab, bind_nav) + table.name + "`</span></p>   <a href=\"#summary\">retour au sommaire</a>\n\n"
    else:
    	text = "## <p id=\"{}\">{}Table: `".format(table.name, bind_nav) + table.name + "` </span></p>   <a href=\"#summary\">retour au sommaire</a>\n\n"

    text += "### Description: \n\n"

    text += table.comment + "\n\n"

    text += "### Columns: \n\n"

    text += "| Column | Data type | Attributes | Default | Description |\n| --- | --- | --- | --- | ---  |\n"

    for column in table.columns:
        text += writeColumnDoc(column, table)

    text += "\n\n"

    if (len(table.indices)):
        text += "### Indices: \n\n"

        text += "| Name | Columns | Type | Description |\n| --- | --- | --- | --- |\n"

        for index in table.indices:
            text += writeIndexDoc(index)

    text += "\n\n"

    return text


def writeColumnDoc(column, table):
    # column name
    text = "| `" + column.name + "`"

    # column type name
    if column.simpleType:
        text += " | " + column.simpleType.name
        # column max lenght if any
        if column.length != -1:
            text += "(" + str(column.length) + ")"
    else:
        text += " | "

    

    text += " | "

    # column attributes
    attribs = [];

    isPrimary = False;
    isUnique = False;
    for index in table.indices:
        if index.indexType == "PRIMARY":
            for c in index.columns:
                if c.referencedColumn.name == column.name:
                    isPrimary = True
                    break
        if index.indexType == "UNIQUE":
            for c in index.columns:
                if c.referencedColumn.name == column.name:
                    isUnique = True
                    break

    # primary?
    if isPrimary:
        attribs.append("PRIMARY")

    # auto increment?
    if column.autoIncrement == 1:
        attribs.append("Auto increments")

    # not null?
    if column.isNotNull == 1:
        attribs.append("Not null")

    # unique?
    if isUnique:
        attribs.append("Unique")

    text += ", ".join(attribs)

    # column default value
    text += " | " + (("`" + column.defaultValue + "`") if column.defaultValue else " ")

    # column description
    text += " | " + (nl2br(column.comment) if column.comment else " ")

    # foreign key
    for fk in table.foreignKeys:
        if fk.columns[0].name == column.name:
            text +=  ("<br /><br />" if column.comment else "") + "**foreign key** de la colonne `" + fk.referencedColumns[0].name + "` de la table `" + fk.referencedColumns[0].owner.name + "`."
            break


    # finish
    text  +=  " |" + "\n"
    return text

def writeIndexDoc(index):

    # index name
    text = "| " + index.name

    # index columns
    text += " | " + ", ".join(map(lambda x: "`" + x.referencedColumn.name + "`", index.columns))

    # index type
    text += " | " + index.indexType

    # index description
    text += " | " + (nl2br(index.comment) if index.comment else " ")

    # finish
    text += " |\n"

    return text

def nl2br(text):
    return "<br />".join(map(lambda x: x.strip(), text.split("\n")))
