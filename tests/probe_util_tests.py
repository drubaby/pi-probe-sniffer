import unittest
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.probe_utils import get_channel_number, get_dBm

mockRadio = """<bound method Packet.mysummary of <RadioTap  version=0 pad=0 len=18
present=Flags+Rate+Channel+dBm_AntSignal+Antenna+RXFlags Flags= Rate=5.5 Mbps
ChannelFrequency=2457 ChannelFlags=CCK+2GHz dBm_AntSignal=-47 dBm Antenna=1 RXFlags= notdecoded=''
|<Dot11  subtype=Probe Request type=Management proto=0 FCfield= ID=0
addr1=ff:ff:ff:ff:ff:ff (RA=DA) addr2=10:3d:1c:cf:3d:61 (TA=SA) addr3=ff:ff:ff:ff:ff:ff (BSSID/STA) SC=13152
|<Dot11ProbeReq  |<Dot11Elt  ID=SSID len=0 info='' |<Dot11EltRates  ID=Supported Rates len=8 rates=[1.0 Mbps, 2.0 Mbps, 5.5 Mbps, 11.0 Mbps, 6.0 Mbps, 9.0 Mbps, 12.0 Mbps, 18.0 Mbps]
|<Dot11EltRates  ID=Extended Supported Rates len=4 rates=[24.0 Mbps, 36.0 Mbps, 48.0 Mbps, 54.0 Mbps]
|<Dot11EltHTCapabilities  ID=HT Capabilities len=26 L_SIG_TXOP_Protection=0 Forty_Mhz_Intolerant=0 PSMP=0 DSSS_CCK=0 Max_A_MSDU=7935 o Delayed_BlockAck=0 Rx_STBC=1 Tx_STBC=1 Short_GI_40Mhz=1
Short_GI_20Mhz=1 Green_Field=0 SM_Power_Save=dynamic SM Supported_Channel_Width=20Mhz+40Mhz LDPC_Coding_Capability=1 res1=0 Min_MPDCU_Start_Spacing=5 Max_A_MPDU_Length_Exponent=3 res2=0
TX_Unequal_Modulation=0 TX_Max_Spatial_Streams=0 TX_RX_MCS_Set_Not_Equal=0 TX_MCS_Set_Defined=0 res3=0 RX_Highest_Supported_Data_Rate=0 res4=0 RX_MSC_Bitmask=65535 res5=0 RD_Responder=0
HTC_HT_Support=0 MCS_Feedback=0 res6=0 PCO_Transition_Time=0 PCO=0 res7=0 Channel_Estimation_Capability=0 CSI_max_n_Rows_Beamformer_Supported=0 Compressed_Steering_n_Beamformer_Antennas_Supported=0
Noncompressed_Steering_n_Beamformer_Antennas_Supported=0 CSI_n_Beamformer_Antennas_Supported=0 Minimal_Grouping=0 Explicit_Compressed_Beamforming_Feedback=0
Explicit_Noncompressed_Beamforming_Feedback=0 Explicit_Transmit_Beamforming_CSI_Feedback=0 Explicit_Compressed_Steering=0 Explicit_Noncompressed_Steering=0 Explicit_CSI_Transmit_Beamforming=0
Calibration=0 Implicit_Trasmit_Beamforming=0 Transmit_NDP=0 Receive_NDP=0 Transmit_Staggered_Sounding=0 Receive_Staggered_Sounding=0 Implicit_Transmit_Beamforming_Receiving=0 ASEL=
|<Dot11Elt  ID=Extendend Capabilities len=14 info='\x04\x00H\\x80\x00@\x00\x00\x00\x00\x00\x00\x00\x00'
|<Dot11Elt  ID=255 len=30 info='#\x01x \n\\xc0\\xab\x0e0\x0e\x00\\xfd\t\\x8c\x0e\x0f\\xfe\x00\\xfa\\xff\\xfa\\xff\\xfa\\xff\\xfa\\xffa\x1c\\xc7q'
|<Dot11Elt  ID=255 len=3 info='\x02\x00\x11'
|<Dot11EltVendorSpecific  ID=Vendor Specific"""


class TestChannel(unittest.TestCase):
    def test_extract_integer(self):
        self.assertEqual(get_channel_number(mockRadio), 10)

    def test_no_colon(self):
        self.assertEqual(get_channel_number("C01 2412Mhz"), 0)

    def test_no_numeric_part(self):
        self.assertEqual(get_channel_number("-->> 2412Mhz"), 0)

    def test_get_dBm(self):
        print(get_dBm(mockRadio))
        self.assertEqual(get_dBm(mockRadio), -47)


if __name__ == "__main__":
    unittest.main()
