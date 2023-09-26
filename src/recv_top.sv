module recv_top #(
    parameter logic [47:0] DEST_MAC_ADDR = 48'h00_0a_95_9d_68_16
) (
    output logic [7:0] out,
    output logic vld,
    output logic ready,

    input logic [7:0] data,
    input logic start,

    input logic clk,
    input logic rst
);

  typedef logic [47:0] mac_addr_t;
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
  logic [3:0] state, next_state;

  always_ff @(posedge clk) begin : stateCounter
    if (rst || state != next_state) begin
      state_counter <= 16'h0;
    end else begin
      state_counter <= state_counter + 16'h1;
    end
  end

  always_ff @(posedge clk) begin : stateRegister
    if (rst) begin
      state <= IDLE;
    end else begin
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
        if (data_q != 8'b1010_1010) begin
          next_state = ERROR;
        end else if (state_counter >= 16'h7 - 16'h1) begin
          next_state = SFD;
        end else begin
          next_state = state;
        end
      end
      SFD: begin
        if (data_q != 8'b1010_1011) begin
          next_state = ERROR;
        end else begin
          next_state = MACDST;
        end
      end
      MACDST: begin
        if (data_q != DEST_MAC_ADDR[state_counter*8+:8]) begin
          next_state = IDLE;
        end else if (state_counter >= 16'h6 - 16'h1) begin
          next_state = MACSRC;
        end else begin
          next_state = state;
        end
      end
      MACSRC: begin
        if (state_counter >= 16'h6 - 16'h1) begin
          next_state = PLLEN;
        end else begin
          next_state = state;
        end
      end
      PLLEN: begin
        if (state_counter >= 16'h2 - 16'h1) begin
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
        end else if (state_counter >= 16'h4 - 16'h1) begin
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
        out   = 8'h0;
        vld   = 1'b0;
        ready = 1'b1;
      end
      PREAMBLE, SFD, MACDST, MACSRC: begin
        out   = 8'h0;
        vld   = 1'b0;
        ready = 1'b0;
      end
      PLLEN, PL, FCS: begin
        out   = data_q6;
        vld   = 1'b1;
        ready = 1'b0;
      end
      SUCCESS: begin
        out   = 8'h0;
        vld   = 1'b1;
        ready = 1'b0;
      end
      ERROR: begin
        out   = {4'hF, state};
        vld   = 1'b1;
        ready = 1'b0;
      end
      default: begin
        out   = 8'h0;
        vld   = 1'b0;
        ready = 1'b0;
      end
    endcase
  end

  always_ff @(posedge clk) begin : nextOutLogic
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
      payload_length[state_counter*8+:8] <= data_q;
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
