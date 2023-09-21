module recv_top (
    output logic [7:0] out,
    output logic vld,
    output logic ready,

    input logic [7:0] data,
    input logic start,

    input logic clk,
    input logic rst
);

  always_ff @(posedge clk) begin
    if (rst) begin
      out   <= 8'b0;
      ready <= 1'b1;
      vld   <= 1'b0;
    end else if (data != 8'hff) begin
      out   <= 8'b0;
      ready <= 1'b0;
      vld   <= 1'b0;
    end else begin
      out   <= data;
      ready <= 1'b0;
      vld   <= 1'b1;
    end
  end

endmodule
