Introduction
============

A tool for Hospital/Resident style matching [NRMP]_, used to pair mentees and
mentors in the Hidden Genius Project. NB: although this project was created
for the `Hidden Genius Project <https://www.hiddengeniusproject.org/>`_ the
algorithm is general purpose and suitable for any Hospital/Resident style
matching problem.

Mentees rank mentors (in a way that allows for ties and indifference); mentors
rank mentees in a similar fashion. The algorithm used in :code:`hgpmatch` pairs mentees
with mentors (subject to mentor capacity constraints) in an unbiased and optimal
fashion.

The match mechanism is *truthful*, meaning that mentees and mentors will get
the best outcomes when ranking each other in a way that reflects their true
preferences, and not how they think they will ultimately match. Said another
way, neither party can "game" the system for a better outcome.

.. [NRMP] https://en.wikipedia.org/wiki/National_Resident_Matching_Program#Matching_algorithm

The :code:`hgpmatch` Tool
=========================

Installation
============

.. code-block:: shell

    pip install hgpmatch

Running
=======

.. code-block:: shell

    hgpmatch [mentee_rankings] [mentor_rankings] [mentor_capacities] [output_path]

The :code:`hgpmatch` expects the path to three csv input files and one output
file as inputs.

The :code:`mentee_rankings` and :code:`mentor_ranking` input files are of the
form:

::

    S1,M2,M1,M3
    S2,M3
    S3,M1,M2,
    S4,M2

Each row represents a mentee (mentor). The first column is the name of that
mentee (mentor) - it can be any arbitrary string. Here we use :code:`S1`, but
it could be :code:`Alice`, :code:`Bob`, or anything else.

Rankings are from left to right, meaning that in this example :code:`S1`
prefers :code:`M2` over all others; their least preferred (ranked) mentor is
:code:`M3`. Note that mentees do not have to rank all mentors and mentors do
not have to rank all mentees. The lack of a ranking indicates *no preference*.
For example, the fact that :code:`S2` did not rank anyone aside from
:code:`M3` indicates that they are ambivalent between the other choices.

The :code:`mentor_capacities` file is of the form:

::

    M1,3
    M2,2
    M3,1

The first column of each row is the name of the mentor. The second is the number
of mentees that they can take on. This number must be a strictly positive
integer; do not include mentors with zero capacity. Note that aggregate mentor
capacity must exceed the total number of students or the solver will warn and
exit without returning a solution.

Running the executable will write a results file to :code:`[output_path]`. The
format of the results file is:

::

    M1,S3
    M2,S1,M2
    M3,S2

The first column of each row is the name of the mentor; subsequent columns
are mentees assigned to that mentor. In the example above, :code:`M1` is
assigned :code:`S3`, :code:`M2` is assigned :code:`S1` and :code:`S2`, etc.

Match Process Formalisms
========================

The match returned represents a stable matching with indifference between
mentors and mentees; more formally, the match (if found) represents a
resident oriented super-stable matching (HRT-Super-Res). See [SWAT]_ for
details.

When no super-stable solutions exist, a fallback solver looks for "good"
weakly-stable matchings; a greedy algorithm expands a ranking poset into a total
ordering in a fashion that biases with weakly-stable matching towards
matches where one party expresses a preference but the other party does not.

.. [SWAT] Irving, R., D. Manlove and S. Scott.
   "The Hospitals/Residents Problem with Ties." SWAT (2000).


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
