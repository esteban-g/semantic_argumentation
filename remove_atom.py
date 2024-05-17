import clingo
import clingox

def main():
    # Initialize the clingo control object
    

    from clingo.symbol import Function
    from clingo.control import Control

    ctl = Control()
    ctl.add("base", [], "a. #external b.")
    ctl.add("base", [], "c :- not f.")
    ctl.ground([("base", [])])
    ctl.assign_external(Function("b"), False)
    print(ctl.solve(on_model=print))

    ctl.release_external(Function("b"))
    print(ctl.solve(on_model=print))

if __name__ == "__main__":
    main()
