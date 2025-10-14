{# THEMODULE #}
{{ node.name }}
{{ '=' * node.name|length }}

.. automodule:: {{ node.name }}
  :no-special-members:

{# SET CURRENT MODULE #}
.. currentmodule:: {{ node.name }}
{# EXCEPTIONS #}
{%- block exceptions -%}
{%- if node.exceptions %}

.. rubric:: Exceptions

{% for item, obj in node.exceptions.items() %}

{% if node.name == obj|module %}
.. autoexception:: {{ item }}
  :no-special-members:
{% else %}
.. exception:: {{ item }}

  See :py:exc:`{{ obj|module }}.{{ obj|qualname }}`.
{% endif %}
{% endfor -%}
{%- endif -%}
{%- endblock -%}
{# CLASSES #}
{%- block classes -%}
{%- if node.classes %}

.. rubric:: Classes

{% for item, obj in node.classes.items() %}

{% if node.name == obj|module %}
.. autoclass:: {{ item }}
  :members:
  :undoc-members:
{% else %}
.. class:: {{ item }}

  See :py:class:`{{ obj|module }}.{{ obj|qualname }}`.
{% endif %}
{% endfor -%}
{%- endif -%}
{%- endblock -%}
{# FUNCTIONS #}
{%- block functions -%}
{%- if node.functions %}

.. rubric:: Functions

{% for item, obj in node.functions.items() %}

{% if node.name == obj|module %}
.. autofunction:: {{ item }}
{% else %}
.. function:: {{ item }}

  See :py:func:`{{ obj|module }}.{{ obj|qualname }}`.
{% endif %}
{% endfor -%}
{%- endif -%}
{%- endblock -%}
{# OBJECTS #}
{%- block objects -%}
{%- if node.variables %}

.. rubric:: Objects

{% for item, obj in node.variables.items() %}

.. autodata:: {{ item }}
  :annotation:

  :Default value:

    .. code-block:: text

      {{ obj|pprint|truncate|indent(6) }}
{% endfor -%}
{%- endif -%}
{%- endblock -%}
{# TOCTREE #}
{%- block toctree -%}
{%- if subnodes %}

.. toctree::
  :hidden:

{% for subnode in subnodes %}
  {{ subnode.name }}
{% endfor -%}
{%- endif -%}
{%- endblock -%}
