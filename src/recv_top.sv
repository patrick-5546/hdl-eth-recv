module recv_top #(
    parameter logic [47:0] DEST_MAC_ADDR = 48'h00_0a_95_9d_68_16
) (
    output logic [7:0] out,
    output logic vld,
    output logic rdy,

    input logic [7:0] data,
    input logic start,

    input logic clk,
    input logic rst
);

  // state lengths
  localparam logic [15:0] PreambleLength = 16'h7;
  localparam logic [15:0] SFDLength = 16'h1;
  localparam logic [15:0] MACLength = 16'h6;
  localparam logic [15:0] PLLenLength = 16'h2;
  localparam logic [15:0] FCSLength = 16'h4;

  // data expected values
  localparam logic [7:0] PreambleOctet = 8'b1010_1010;
  localparam logic [7:0] SFDOctet = 8'b1010_1011;

  typedef enum logic [3:0] {
    IDLE,
    PREAMBLE,
    SFD,
    MACDST,
    MACSRC,
    PLLEN,
    PL,
    FCS,
    SUCCESS,
    ERROR
  } state_t;

  logic [15:0] payload_length, state_counter;
  logic [7:0] data_q, data_q1, data_q2, data_q3, data_q4, data_q5, data_q6;
  logic [7:0] lrc;
  logic [3:0] state, next_state, last_state;

  always_ff @(posedge clk) begin : stateCounter
    if (rst || state != next_state) begin
      state_counter <= 16'h0;
    end else begin
      state_counter <= state_counter + 16'h1;
    end
  end

  always_ff @(posedge clk) begin : stateRegister
    if (rst) begin
      last_state <= IDLE;
      state <= IDLE;
    end else begin
      last_state <= state;
      state <= next_state;
    end
  end

  always_comb begin : nextStateLogic
    case (state)
      IDLE: begin
        if (start) begin
          next_state = PREAMBLE;
        end else begin
          next_state = state;
        end
      end
      PREAMBLE: begin
        if (data_q != PreambleOctet) begin
          next_state = ERROR;
        end else if (state_counter >= PreambleLength - 16'h1) begin
          next_state = SFD;
        end else begin
          next_state = state;
        end
      end
      SFD: begin
        if (data_q != SFDOctet) begin
          next_state = ERROR;
        end else if (state_counter >= SFDLength - 16'h1) begin
          next_state = MACDST;
        end else begin
          next_state = state;
        end
      end
      MACDST: begin
        if (data_q != DEST_MAC_ADDR[(5-state_counter)*8+:8]) begin
          next_state = IDLE;
        end else if (state_counter >= MACLength - 16'h1) begin
          next_state = MACSRC;
        end else begin
          next_state = state;
        end
      end
      MACSRC: begin
        if (state_counter >= MACLength - 16'h1) begin
          next_state = PLLEN;
        end else begin
          next_state = state;
        end
      end
      PLLEN: begin
        if (state_counter >= PLLenLength - 16'h1) begin
          next_state = PL;
        end else begin
          next_state = state;
        end
      end
      PL: begin
        if (state_counter >= payload_length - 16'h1) begin
          next_state = FCS;
        end else begin
          next_state = state;
        end
      end
      FCS: begin
        if (data_q != (lrc ^ 8'hFF) + 1) begin
          next_state = ERROR;
        end else if (state_counter >= FCSLength - 16'h1) begin
          next_state = SUCCESS;
        end else begin
          next_state = state;
        end
      end
      SUCCESS: next_state = IDLE;
      ERROR:   next_state = IDLE;
      default: next_state = IDLE;
    endcase
  end

  always_comb begin : outputLogic
    case (state)
      IDLE: begin
        out = 8'h0;
        vld = 1'b0;
        rdy = 1'b1;
      end
      PREAMBLE, SFD, MACDST, MACSRC: begin
        out = 8'h0;
        vld = 1'b0;
        rdy = 1'b0;
      end
      PLLEN: begin
        out = data_q6;
        vld = 1'b1;
        rdy = 1'b0;
      end
      PL: begin
        out = (state_counter >= 4) ? data_q4 : data_q6;
        vld = 1'b1;
        rdy = 1'b0;
      end
      FCS: begin
        out = data_q4;
        vld = 1'b1;
        rdy = 1'b0;
      end
      SUCCESS: begin
        out = 8'h0;
        vld = 1'b1;
        rdy = 1'b0;
      end
      ERROR: begin
        out = {4'hF, last_state};
        vld = 1'b1;
        rdy = 1'b0;
      end
      default: begin
        out = 8'h0;
        vld = 1'b0;
        rdy = 1'b0;
      end
    endcase
  end

  always_ff @(posedge clk) begin : delayLogic
    if (!rst && (state == MACSRC || state == PLLEN || state == PL || state == FCS)) begin
      data_q  <= data;
      data_q1 <= data_q;
      data_q2 <= data_q1;
      data_q3 <= data_q2;
      data_q4 <= data_q3;
      data_q5 <= data_q4;
      data_q6 <= data_q5;
    end else if (!rst) begin
      data_q  <= data;
      data_q1 <= 8'h0;
      data_q2 <= 8'h0;
      data_q3 <= 8'h0;
      data_q4 <= 8'h0;
      data_q5 <= 8'h0;
      data_q6 <= 8'h0;
    end else begin
      data_q  <= 8'h0;
      data_q1 <= 8'h0;
      data_q2 <= 8'h0;
      data_q3 <= 8'h0;
      data_q4 <= 8'h0;
      data_q5 <= 8'h0;
      data_q6 <= 8'h0;
    end
  end

  always_ff @(posedge clk) begin : payloadLengthLogic
    if (!rst && (state == PLLEN)) begin
      payload_length[(1-state_counter)*8+:8] <= data_q;
    end else if (!rst && (state == PL)) begin
      payload_length <= payload_length;
    end else begin
      payload_length <= 16'h0;
    end
  end

  always_ff @(posedge clk) begin : lrcLogic
    if (!rst && (state == MACDST || state == MACSRC || state == PLLEN || state == PL)) begin
      lrc <= lrc + data_q;
    end else if (!rst && state == FCS) begin
      lrc <= lrc;
    end else begin
      lrc <= 8'h0;
    end
  end

endmodule
