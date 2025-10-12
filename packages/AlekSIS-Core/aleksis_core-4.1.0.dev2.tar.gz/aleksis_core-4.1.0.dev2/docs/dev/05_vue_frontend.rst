Vue-based frontend
==================

The AlekSIS frontend is based on the `Vue.js`_ framework and the `Vuetify`_ UI library.
It communicates with the backend using a `GraphQL` API.


CRUD
----

In a nutshell: Use the ``CRUDProvider`` component, because it is flexible and provides you with just what you need.

If you give it a query, it will by default display the results in an inline CRUD list, setting ``disable-inline-edit`` makes this a normal CRUD list. If you want another form of display, put it in the ``view`` slot. The ``view`` slot has extra functionality provided by the ``CRUDController``: selection, actions, and search. If you don't need these, use the ``body`` slot instead.

If you provide create/patch/delete mutations, you get the respective widgets and can use them from the ``view`` and ``body`` slots.

If you don't need any of the ``CRUDProvider``'s components and just want
to do CRUD in your code, you can directly use the ``useCRUD`` composable instead.

Furthermore, you can access the CRUD object returned by ``useCRUD`` in the ``view`` and ``body`` slots.

To see what you can use in the different slots of the ``CRUDProvider``, look at their ``attrs`` object.

Object Schemas
^^^^^^^^^^^^^^

The ``CRUDProvider`` can take most of its options directly from the object schema. The object schema lives in the ``objectSchema.js`` file in an app's ``frontend`` directory and completly specifies the CRUD interface for each GraphQL object type, which most likely directly corresponds to a Django model.

This means to get a simple inline CRUD list, you just have to provide the ``CRUDProvider`` component with an ``objectType``:

.. code-block:: vue

  <c-r-u-d-provider :object-schema="{ type: 'RoomType' }" />

And yes this is the actual RoomList. In the objectSchema passed directly to the CRUDProvider you can set anything you want and it will overwrite the general objectSchema in objectSchema.js.

The objectSchema has a rigorous base structure, but is quite loose in what it allows to be build on top. Its properties are passed around widely and are therefore available in the CRUD components and slots. If you have a configuration you want to add, consider adding it to the ``objectSchema`` to make it generally available.
