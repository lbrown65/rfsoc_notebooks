-- -------------------------------------------------------------
-- 
-- File Name: hdl_prj\hdlsrc\axis_controller\AxisController_src_AXI_Stream_Controller.vhd
-- Created: 2021-02-09 13:59:38
-- 
-- Generated by MATLAB 9.8 and HDL Coder 3.16
-- 
-- 
-- -------------------------------------------------------------
-- Rate and Clocking Details
-- -------------------------------------------------------------
-- Model base rate: 0.2
-- Target subsystem base rate: 0.2
-- 
-- 
-- Clock Enable  Sample Time
-- -------------------------------------------------------------
-- ce_out        0.2
-- -------------------------------------------------------------
-- 
-- 
-- Output Signal                 Clock Enable  Sample Time
-- -------------------------------------------------------------
-- m_axis_tdata                  ce_out        0.2
-- m_axis_tvalid                 ce_out        0.2
-- -------------------------------------------------------------
-- 
-- -------------------------------------------------------------


-- -------------------------------------------------------------
-- 
-- Module: AxisController_src_AXI_Stream_Controller
-- Source Path: axis_controller/AXI-Stream Controller
-- Hierarchy Level: 0
-- 
-- -------------------------------------------------------------
LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

ENTITY AxisController_src_AXI_Stream_Controller IS
  PORT( clk                               :   IN    std_logic;
        reset                             :   IN    std_logic;
        clk_enable                        :   IN    std_logic;
        Enable                            :   IN    std_logic_vector(31 DOWNTO 0);  -- uint32
        Value                             :   IN    std_logic_vector(31 DOWNTO 0);  -- uint32
        m_axis_tready                     :   IN    std_logic;
        ce_out                            :   OUT   std_logic;
        m_axis_tdata                      :   OUT   std_logic_vector(127 DOWNTO 0);  -- ufix128
        m_axis_tvalid                     :   OUT   std_logic
        );
END AxisController_src_AXI_Stream_Controller;


ARCHITECTURE rtl OF AxisController_src_AXI_Stream_Controller IS

  -- Signals
  SIGNAL enb                              : std_logic;
  SIGNAL Enable_unsigned                  : unsigned(31 DOWNTO 0);  -- uint32
  SIGNAL Bit_Slice_out1                   : std_logic;  -- ufix1
  SIGNAL Constant_out1                    : unsigned(127 DOWNTO 0);  -- ufix128
  SIGNAL Value_unsigned                   : unsigned(31 DOWNTO 0);  -- uint32
  SIGNAL Bit_Concat_out1                  : unsigned(127 DOWNTO 0);  -- ufix128
  SIGNAL Multiport_Switch_out1            : unsigned(127 DOWNTO 0);  -- ufix128
  SIGNAL Delay_out1                       : std_logic;

BEGIN
  Enable_unsigned <= unsigned(Enable);

  Bit_Slice_out1 <= Enable_unsigned(0);

  Constant_out1 <= to_unsigned(0, 128);

  Value_unsigned <= unsigned(Value);

  Bit_Concat_out1 <= Value_unsigned & Value_unsigned & Value_unsigned & Value_unsigned;

  
  Multiport_Switch_out1 <= Constant_out1 WHEN Bit_Slice_out1 = '0' ELSE
      Bit_Concat_out1;

  m_axis_tdata <= std_logic_vector(Multiport_Switch_out1);

  enb <= clk_enable;

  Delay_process : PROCESS (clk, reset)
  BEGIN
    IF reset = '1' THEN
      Delay_out1 <= '0';
    ELSIF clk'EVENT AND clk = '1' THEN
      IF enb = '1' THEN
        Delay_out1 <= m_axis_tready;
      END IF;
    END IF;
  END PROCESS Delay_process;


  ce_out <= clk_enable;

  m_axis_tvalid <= Delay_out1;

END rtl;
