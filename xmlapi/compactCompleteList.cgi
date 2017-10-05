#!/bin/tclsh
################################################################################
# List all devices, channels, datapoints, rooms and functions in one request   #
# and in a minimalistic and compact XML structure in which the tags and        #
# attributes consist of only 1 to 2 letters.                                   #
# The channels and attributes are reduced to the minimum required for remote   #
# control of the CCU.                                                          #
#                                                                              #
# It is primarily intended to minimize data transfer on mobile devices and     #
# still enjoy the comfort of XML.                                              #
#                                                                              #
# The Script is based on devicelist.cgi, statelist.cgi, roomlist.cgi and       #
# functionlist.cgi.                                                            #
################################################################################

load tclrega.so
puts -nonewline {Content-Type: text/xml
Access-Control-Allow-Origin: *

<?xml version="1.0" encoding="ISO-8859-1" ?><all>}

array set res [rega_script {
  !*****************************************************************************
  ! List devices, channels and datapoints
  !*****************************************************************************

  Write("<dl>");

  string sDevId;
  string sChnId;
  string sDPId;

  foreach (sDevId, root.Devices().EnumUsedIDs()) {
    object  oDevice   = dom.GetObject(sDevId);
    boolean bDevReady = oDevice.ReadyConfig();
    if (true == bDevReady) {
      string sDevType = oDevice.HssType();
      if ( ("HMW-RCV-50" != sDevType) && ("HM-RCV-50" != sDevType) ) {
        Write("<d");
        Write(" n='"); WriteXML( oDevice.Name() ); Write("'");
        Write(" i='" # sDevId # "'");
        Write(" t='"); WriteXML(sDevType); Write("'");
        Write(">");

        foreach(sChnId, oDevice.Channels()) {

          object oChannel = dom.GetObject(sChnId);
          integer iChnDir = oChannel.ChnDirection();
          string  sChnDir = "U";
          string  sChnShow = "";

          if (1 == iChnDir) { sChnDir = "S"; }
          if (2 == iChnDir) { sChnDir = "R"; }

          if (false == oChannel.Internal()) {
            if (oChannel.Visible()) {
              sChnShow = "1";
            } else {
              sChnShow = "0";
            }
          }

          Write("<c n='"); WriteXML( oChannel.Name() ); Write("'");
          Write(" i='" # sChnId # "'");
          Write(" d='" # sChnDir # "'");
          Write(" x='" # oChannel.ChnNumber() # "'");
          Write(" s='" # sChnShow # "'");

          Write(">");

          foreach (sDPId, oChannel.DPs().EnumUsedIDs()) {
            object oDP = dom.GetObject(sDPId);
            if (oDP) {
              string sDp = oDP.Name().StrValueByIndex(".", 2);
              string sPart0 = sDp.StrValueByIndex("_", 0);

              if ( (sPart0 != "CMD") &&
                   (sPart0 != "ERROR") &&
                   (sPart0 != "RSSI") &&
                   (sDp != "ON_TIME") &&
                   (sDp != "INHIBIT") &&
                   (sDp != "UNREACH") &&
                   (sDp != "STICKY_UNREACH") &&
                   (sDp != "CONFIG_PENDING") &&
                   (sDp != "DEVICE_IN_BOOTLOADER") &&
                   (sDp != "UPDATE_PENDING") &&
                   (sDp != "DUTY_CYCLE") ) {
                Write("<p");
                Write(" t='"); WriteXML(sDp);
                Write("' i='" # sDPId );
                Write("' v='"); WriteXML(oDP.Value());
                Write("'/>");
              }
            }
          }

          Write("</c>");
        }

        Write("</d>");
      }
    }
  }

  Write("</dl>");

  !*****************************************************************************
  ! List rooms
  !*****************************************************************************

  Write("<rl>");

  object oRoom;
  string sRoomId;
  string sRoomName;
  string sChannelId;

  foreach (sRoomId, dom.GetObject(ID_ROOMS).EnumUsedIDs()) {
    oRoom = dom.GetObject(sRoomId);

    Write("<r n='"); WriteXML( oRoom.Name() );
    Write("' i='" # sRoomId # "'>");

    foreach (sChannelId, oRoom.EnumUsedIDs()) {
      Write("<c i='" # sChannelId # "'/>");
    }

    Write("</r>");
  }

  Write("</rl>");

  !*****************************************************************************
  ! List functions
  !*****************************************************************************

  Write("<fl>");

  object oFunction;
  string sFunctionId;
  string sChannelId;

  foreach (sFunctionId, dom.GetObject(ID_FUNCTIONS).EnumUsedIDs()) {
    oFunction     = dom.GetObject(sFunctionId);

    Write("<f n='"); WriteXML( oFunction.Name() );
    Write("' i='" # sFunctionId # "'>");

    foreach (sChannelId, oFunction.EnumUsedIDs()) {
        Write("<c i='" # sChannelId # "'/>");
    }

    Write("</f>");
  }

  Write("</fl>");

}]

puts -nonewline $res(STDOUT)
puts -nonewline {</all>}
