function wrapped_sin
  input Real x;
  input String name;
  output Real Value;

  external "C" Value = sin(x) annotation(
    Include = "#include <math.h>"
  );
end wrapped_sin;

function my_sin
  input Real first_quantity;
  output Real Value;

algorithm
  assert(1 < 2, "my_sin has failed.");
  Value := wrapped_sin(first_quantity, "banana");
end my_sin;

model TestModel
  Real y = my_sin(3.14);
end TestModel;

