# Semantic-based Arguments' Construction

This project is for the development of a strucutred argumentation framework based on reqriting systems.

Summary of the Semantic-based Arguments via Logic Programming Rewriting Systems

Formal argumentation frameworks traditionally emphasize constructing structural arguments
from rules with well-supported deductive evidence. Differently from other approaches, this research emphasizes the role of investigating general frameworks that can also provide a consistent and well-defined justification for a conclusion that cannot be inferred and there is certainty about it, that we call here NAF arguments, which have been less explored in the formal argumentation theory, despite its potential use in practical applications for justifying atoms where no deductive evidence exists. Few current approaches disregard key characteristics of well-defined arguments, such as consistency (avoiding internal argument contradictions), relatedness (conclusions based on relevant information), and minimality (using the least amount of information necessary). This article introduces the so-called confluent argumentation guaranteeing these quality argumentation characteristics and the ability to justify both “positive” and “negative” conclusions by the so-called confluent and NAF arguments. This framework is defined in terms of Confluent LP Systems as rewriting systems on the set of all logic programs, making this approach a general framework. Additionally, we introduce a method for building such arguments using the program’s strata through partial interpretations, leading to a more efficient process compared to analyzing dependency graphs of atoms. 

KEYWORDS: Structural arguments, formal argumentation, rewriting systems, logic programming


Disclaimer: Writing: this is not very well tested, there might be
bugs.

## Dependencies

This project needs the Python libraries:
- Clingo 
- Clingox 
- Networkx 


# Example of programs and calls

    t2.lp = \{
        e:-  not u.
        t:- not  s.
        a :- b.
        b.}

    

    python.exe .\wfs2.py .\t2.lp
