<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
	xmlns:m="http://rep.oio.dk/medcom.dk/xml/schemas/2016/10/02/" 
	xmlns:cpr="http://rep.oio.dk/cpr.dk/xml/schemas/core/2002/06/28/" 
	xmlns:dkcc="http://rep.oio.dk/ebxml/xml/schemas/dkcc/2003/02/13/" 
	xmlns:xs="http://www.w3.org/2001/XMLSchema">
	<xsl:output media-type="text/html"/>

	<!-- 
		ReferralAttachment (BIN02) 
	-->
	<xsl:template match="m:Emessage[m:ReferralAttachment]">
		<xsl:for-each select="m:ReferralAttachment">
			<xsl:variable name="SenderEAN" select="m:Sender/m:EANIdentifier"/>
			<td valign="top" width="100%" bgcolor="#ffffff" colspan="2">
				<table width="100%">
					<tbody>
						<tr>
							<xsl:call-template name="ShowMessageHeader">
								<xsl:with-param name="MessageName" select=" 'Henvisningsbilag (BIN02)' "/>
							</xsl:call-template>
						</tr>
						<xsl:for-each select="m:BinaryObject">
							<tr>
								<td>ObjektRefnr: <xsl:value-of select="m:ObjectIdentifier"/></td>
							</tr>
							<tr>
								<td>
									<xsl:attribute name="bgcolor"><xsl:value-of select="$compoundbgcolor"/></xsl:attribute>
									<xsl:variable name="OC" select="m:ObjectCode"/>
									<xsl:variable name="OEC" select="m:ObjectExtensionCode"/>
									<xsl:variable name="icon">
										<xsl:choose>
											<xsl:when test="$OEC='doc'">
												<xsl:value-of select="'img/wordicon.GIF'"/>
											</xsl:when>
											<xsl:when test="$OC='multimedie'">
												<xsl:value-of select="'img/multiicon.GIF'"/>
											</xsl:when>
											<xsl:otherwise>
												<xsl:value-of select="'img/binicon.PNG'"/>
											</xsl:otherwise>
										</xsl:choose>
									</xsl:variable>
									<xsl:choose>
										<xsl:when test="$OC='billede'">
											<img>
												<xsl:attribute name="src"><xsl:value-of select="concat('Binary/',$SenderEAN,'_',m:ObjectIdentifier,'_',m:ObjectCode,'.',m:ObjectExtensionCode)"/></xsl:attribute>
											</img>
										</xsl:when>
										<xsl:when test="$OC='multimedie'">
											<object ID="MediaPlayer1" classid="CLSID:22D6F312-B0F6-11D0-94AB-0080C74C7E95" codebase="http://activex.microsoft.com/activex/controls/mplayer/en/nsmp2inf.cab#Version=5,1,52,701" standby="Loading Microsoft® Windows® Media Player components..." type="application/x-oleobject">
												<param name="AudioStream" value="true"/>
												<param name="AutoSize" value="true"/>
												<param name="AutoStart" value="0"/>
												<param name="AnimationAtStart" value="true"/>
												<param name="AllowScan" value="true"/>
												<param name="AllowChangeDisplaySize" value="true"/>
												<param name="AutoRewind" value="0"/>
												<param name="Balance" value="0"/>
												<param name="BaseURL" value=""/>
												<param name="BufferingTime" value="5"/>
												<param name="CaptioningID" value=""/>
												<param name="ClickToPlay" value="true"/>
												<param name="CursorType" value="1"/>
												<param name="CurrentPosition" value="true"/>
												<param name="CurrentMarker" value="0"/>
												<param name="DefaultFrame" value=""/>
												<param name="DisplayBackColor" value="0"/>
												<param name="DisplayForeColor" value="16777215"/>
												<param name="DisplayMode" value="0"/>
												<param name="DisplaySize" value="0"/>
												<param name="Enabled" value="true"/>
												<param name="EnableContextMenu" value="0"/>
												<param name="EnablePositionControls" value="true"/>
												<param name="EnableFullScreenControls" value="true"/>
												<param name="EnableTracker" value="true"/>
												<param name="Filename">
													<xsl:attribute name="value"><xsl:value-of select="concat('Binary/',$SenderEAN,'_',m:ObjectIdentifier,'_',m:ObjectCode,'.',m:ObjectExtensionCode)"/></xsl:attribute>
												</param>
												<param name="InvokeURLs" value="true"/>
												<param name="Language" value="true"/>
												<param name="Mute" value="0"/>
												<param name="PlayCount" value="1"/>
												<param name="PreviewMode" value="0"/>
												<param name="Rate" value="1"/>
												<param name="SAMILang" value=""/>
												<param name="SAMIStyle" value=""/>
												<param name="SAMIFileName" value=""/>
												<param name="SelectionStart" value="true"/>
												<param name="SelectionEnd" value="true"/>
												<param name="SendOpenStateChangeEvents" value="true"/>
												<param name="SendWarningEvents" value="true"/>
												<param name="SendErrorEvents" value="true"/>
												<param name="SendKeyboardEvents" value="0"/>
												<param name="SendMouseClickEvents" value="0"/>
												<param name="SendMouseMoveEvents" value="0"/>
												<param name="SendPlayStateChangeEvents" value="true"/>
												<param name="ShowCaptioning" value="0"/>
												<param name="ShowControls" value="true"/>
												<param name="ShowAudioControls" value="true"/>
												<param name="ShowDisplay" value="0"/>
												<param name="ShowGotoBar" value="0"/>
												<param name="ShowPositionControls" value="true"/>
												<param name="ShowStatusBar" value="true"/>
												<param name="ShowTracker" value="0"/>
												<param name="TransparentAtStart" value="0"/>
												<param name="VideoBorderWidth" value="0"/>
												<param name="VideoBorderColor" value="0"/>
												<param name="VideoBorder3D" value="0"/>
												<param name="Volume" value="-600"/>
												<param name="WindowlessVideo" value="0"/>
												<embed type="application/x-mplayer2" pluginspage="http://www.microsoft.com/Windows/MediaPlayer/" autostart="0" showcontrols="0">
													<xsl:attribute name="src"><xsl:value-of select="concat('Binary/',$SenderEAN,'_',m:ObjectIdentifier,'_',m:ObjectCode,'.',m:ObjectExtensionCode)"/></xsl:attribute>
												</embed>
											</object>
										</xsl:when>
										<xsl:otherwise>
											<img>
												<xsl:attribute name="src"><xsl:value-of select="$icon"/></xsl:attribute>
											</img>
											<a target="newwindow">
												<xsl:attribute name="href"><xsl:value-of select="concat('Binary/',$SenderEAN,'_',m:ObjectIdentifier,'_',m:ObjectCode,'.',m:ObjectExtensionCode)"/></xsl:attribute>
												<xsl:value-of select="concat(m:ObjectIdentifier,' (',m:OriginalObjectSize,' bytes)')"/>
											</a>
										</xsl:otherwise>
									</xsl:choose>
								</td>
							</tr>
						</xsl:for-each>
						<tr>
							<xsl:call-template name="ShowPatientAndRelatives"/>
						</tr>
						<tr>
							<xsl:call-template name="ShowParticipants"/>
						</tr>
					</tbody>
				</table>
			</td>
		</xsl:for-each>
	</xsl:template>
 
</xsl:stylesheet>
