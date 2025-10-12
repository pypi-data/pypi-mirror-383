
model WorkingModel
  Real x;
  Real y;
equation
  der(x) = y
  y = 2*x;
end WorkingModel;