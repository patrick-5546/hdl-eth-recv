module recv_top (
    input  logic clk,
    d,
    output logic q
);

  always_ff @(clk) begin
    q = d;
  end

endmodule
