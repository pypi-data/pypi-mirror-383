model IncorrectModel
  Real x(start=1.0); // Initial value for 'x' is not allowed
  Real y;
equation
  y = x + z; // 'z' is not declared
end IncorrectModel;