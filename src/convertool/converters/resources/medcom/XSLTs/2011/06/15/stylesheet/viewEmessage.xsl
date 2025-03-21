<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:m="http://rep.oio.dk/medcom.dk/xml/schemas/2011/06/15/"
	xmlns:cpr="http://rep.oio.dk/cpr.dk/xml/schemas/core/2002/06/28/"
	xmlns:dkcc="http://rep.oio.dk/ebxml/xml/schemas/dkcc/2003/02/13/"
	xmlns:xs="http://www.w3.org/2001/XMLSchema">
	<xsl:output media-type="text/html"/>

	<xsl:include href="WebReport.xsl"/>

	<xsl:template name="ShowReqStatus_XR0531M">
		<td valign="top">
			<b>Status:</b>
		</td>
		<td valign="top">
			<xsl:variable name="RS" select="m:LaboratoryResults/m:GeneralResultInformation/m:ResultStatus"/>
			<table border="0">
				<tbody>
					<tr>
						<xsl:choose>
							<xsl:when test="$RS='komplet'">
								<td valign="top">Komplet svar</td>
								<td><img src="img/Ikon_Komplet.PNG"></img></td>
							</xsl:when>
							<xsl:when test="$RS='delvis'">
								<td valign="top">Delsvar</td>
								<td><img src="img/Ikon_Delsvar.PNG"></img></td>
							</xsl:when>
							<xsl:when test="$RS='modtaget'">
								<td valign="top">Prøvemodtaget</td>
								<td><img src="img/Ikon_Modtaget.PNG"></img></td>
							</xsl:when>
							<xsl:otherwise>
								<td>Bestilt</td>
							</xsl:otherwise>
						</xsl:choose>
					</tr>
				</tbody>
			</table>
		</td>
	</xsl:template>

</xsl:stylesheet>
