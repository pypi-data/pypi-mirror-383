from ntsim.Propagator import Propagator


class propagator1(Propagator):
    def propagate(self,input: dict) -> dict:
        out = {'p1':'output data'}
        print(input,out)
        return out
    def configure(self,opts):
        print(opts)

class propagator2(Propagator):
    def propagate(self,input: dict) -> dict:
        out = {'p2':'output data'}
        print(input,out)
        return out
    def configure(self,opts):
        print(opts)

p1 = propagator1()
p2 = propagator2()
propagators = [p1,p2]
input = {'input data to p1'}
for p in propagators:
    input = p.propagate(input=input)
