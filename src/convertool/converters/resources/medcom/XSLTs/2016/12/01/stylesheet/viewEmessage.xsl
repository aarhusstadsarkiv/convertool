<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:m="http://rep.oio.dk/medcom.dk/xml/schemas/2016/12/01/" xmlns:gepj="http://medinfo.dk/epj/proj/gepka/20030701/xml/schema" xmlns:cpr="http://rep.oio.dk/cpr.dk/xml/schemas/core/2002/06/28/" xmlns:dkcc="http://rep.oio.dk/ebxml/xml/schemas/dkcc/2003/02/13/" xmlns:xs="http://www.w3.org/2001/XMLSchema">
	<xsl:output media-type="text/html"/>

	<!-- 	MunicipalityLetter -->
	<xsl:template match="m:Emessage[m:MunicipalityLetter]">
		<xsl:for-each select="m:MunicipalityLetter">
			<td valign="top" width="100%" bgcolor="#ffffff" colspan="2">
				<table width="100%">
					<tbody>
						<tr>
							<xsl:call-template name="ShowMessageHeader">
								<xsl:with-param name="MessageName" select="'Afslutningsnotat fra kommunal forebyggelse'"/>
							</xsl:call-template>
						</tr>
						<tr>
							<td valign="top" width="100%">
								<table>
									<tbody>
										<tr>
											<td valign="top">
												<b>Henvisningsdato<!--stidspunkt-->:</b>
											</td>
											<td valign="top">
												<xsl:for-each select="m:Admission">
													<xsl:call-template name="FormatDateTime"/>
												</xsl:for-each>
											</td>
											<td valign="top">
												<b>Afslutningsdato<!--stidspunkt-->:</b>
											</td>
											<td valign="top">
												<xsl:for-each select="m:Discharge">
													<xsl:call-template name="FormatDateTime"/>
												</xsl:for-each>
											</td>
										</tr>
									</tbody>
								</table>
							</td>
						</tr>
						<xsl:if test="count(m:Referral)>0">
							<tr>
								<td valign="top" width="100%">
									<table>
										<tbody>
											<tr>
											
												<td valign="top">
													<b>
												Diagnoser
											</b>
												</td>
											</tr>
											<tr>
												<td>
													<table>
														<tbody>
															
															<xsl:for-each select="m:Referral/m:Refer">
																<tr>
																	<td valign="top">
																		<b>Diagnose:</b>
																	</td>
																	<td valign="top">
																		<xsl:value-of select="m:DiagnoseCode"/>
																	</td>
																	<td valign="top">
																		<xsl:value-of select="m:DiagnoseTypeCode"/>
																	</td>
																	<td valign="top">
																		<xsl:value-of select="m:DiagnoseText"/>
																	</td>
																</tr>
															</xsl:for-each>
															<xsl:for-each select="m:Referral/m:ReferralAdditional">
																<tr>
																	<td valign="top">
																		<b>Bidiagnose:</b>
																	</td>
																	<td valign="top">
																		<xsl:value-of select="m:DiagnoseCode"/>:
																	</td>
																	<td valign="top">
																		<xsl:value-of select="m:DiagnoseTypeCode"/>
																	</td>
																	<td valign="top">
																		<xsl:value-of select="m:DiagnoseText"/>
																	</td>
																	<td valign="top">
																		<xsl:for-each select="m:DiagnoseDateTime">
																			<xsl:call-template name="FormatDateTime"/>
																		</xsl:for-each>
																	</td>
																</tr>
															</xsl:for-each>
														</tbody>
													</table>
												</td>
											</tr>
										</tbody>
									</table>
								</td>
							</tr>
						</xsl:if>
						<tr>
							<td valign="top" width="100%">
								<table>
									<tbody>
										<tr>
											<td valign="top">
												<b>
												Epikrise
											</b>
											</td>
										</tr>
										<tr>
											<td valign="top">
												<table>
													<tbody>
														<xsl:for-each select="m:ClinicalInformation">
															<tr>
																
																<td valign="top">
																	<xsl:for-each select="m:Text01">
																		<xsl:apply-templates/>
																	</xsl:for-each>
																</td>
																</tr>
														</xsl:for-each>
														
														</tbody>
												</table>
											</td>
										</tr>
									</tbody>
								</table>
							</td>
						</tr>
						<td valign="top" width="100%">
							<table>
								<tbody>
									<tr>
										<td valign="top">
											<table>
												<tbody>
													<td valign="top">
														<xsl:for-each select="m:ClinicalInformation/m:Signed">
															
															
															<tr>
																<td valign="top">
																	<b>Underskrevet af:</b>
																</td>
																<td valign="top">
																	<xsl:value-of select="m:JobTitle"/>
																</td>
																<td valign="top">
																	<xsl:value-of select="m:SignedBy"/>
																</td>
																<td valign="top">
																	
																</td>
																<td valign="top">
																	<xsl:value-of select="m:Date"/>
																</td>
															</tr>
														</xsl:for-each>
													</td> 
												</tbody>
											</table>
										</td>
									</tr>
								</tbody>
							</table>
						</td>
						<tr>
							<xsl:call-template name="showReferences">
								<xsl:with-param name="SenderEAN" select="m:Sender/m:EANIdentifier"/>
							</xsl:call-template>
						</tr>
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
	
			
	
	<!--	MunicipalityReferral -->
	<xsl:template match="m:Emessage[m:MunicipalityReferral]">
		<xsl:for-each select="m:MunicipalityReferral">
			<td valign="top" width="100%" bgcolor="#ffffff" colspan="2">
				<table width="100%">
					<tbody>
						<tr>
							<xsl:call-template name="ShowMessageHeader">
								<xsl:with-param name="MessageName" select="'Henvisning til kommunal forebyggelse'"/>
							</xsl:call-template>
						</tr>
						
						<xsl:if test="count(m:Referral)>0">
							<tr>
								<td valign="top" width="100%">
									<table>
										<tbody>
											<tr>
												<td valign="top">
													<b>
												Henvisnings diagnoser
											</b>
												</td>
											</tr>
											<tr>
												<td>
													<table>
														<tbody>
															<xsl:for-each select="m:Referral/m:Refer">
																<tr>
																	<td valign="top">
																		<b>Hoveddiagnose:</b>
																	</td>
																	<td valign="top">
																		<xsl:value-of select="m:DiagnoseCode"/>
																	</td>
																	<td valign="top">
																		<xsl:value-of select="m:DiagnoseText"/>
																	</td>
																</tr>
															</xsl:for-each>
															<xsl:for-each select="m:Referral/m:ReferralAdditional">
																<tr>
																	<td valign="top">
																		<xsl:value-of select="m:DiagnoseDescriptionCode"/>:
																	</td>
																	<td valign="top">
																		<xsl:value-of select="m:DiagnoseCode"/>
																	</td>
																	<td valign="top">
																		<xsl:value-of select="m:DiagnoseText"/>
																	</td>
																</tr>
															</xsl:for-each>
														</tbody>
													</table>
												</td>
											</tr>
										</tbody>
									</table>
								</td>
							</tr>
						</xsl:if>
						
						<tr>
							<td valign="top" width="100%">
								<table width="100%">
									<tbody>
										<tr>
											<td valign="top" width="100%">
												<b>
												Kliniske oplysninger
											</b>
											</td>
										</tr>
										<tr>
											<xsl:attribute name="bgcolor"><xsl:value-of select="$compoundbgcolor"/></xsl:attribute>
											<td valign="top" width="100%">
												<table width="100%">
													<tbody>
														<xsl:for-each select="m:RelevantClinicalInformation/m:Anamnesis">
															<tr>
																<td>
																	<table>
																		<tbody>
																			<tr>
																				<td valign="top">
																					<xsl:apply-templates/>
																				</td>
																			</tr>
																		</tbody>
																	</table>
																</td>
															</tr>
														</xsl:for-each>
													</tbody>
												</table>
											</td>
										</tr>
									</tbody>
								</table>
							</td>
						</tr>
						<tr>
							<xsl:call-template name="showReferences">
								<xsl:with-param name="SenderEAN" select="m:Sender/m:EANIdentifier"/>
							</xsl:call-template>
						</tr>
						<xsl:if test="count(m:MunicipalityVisitation)>0">
							<tr>
								<td valign="top" width="100%">
									<table>
										<tbody>
											<tr>
												<td valign="top">
													<b>Visitation (udfyldt af modtager)</b>
												</td>
											</tr>
											<tr>
												<td valign="top">
													<table>
														<tbody>
															<xsl:for-each select="m:MunicipalityVisitation">
																<tr>
																	<td valign="top">
																		<xsl:value-of select="m:InformationCode"/>
																	</td>
																	<td valign="top">
																		<xsl:for-each select="m:Information">
																			<xsl:apply-templates/>
																		</xsl:for-each>
																	</td>
																</tr>
															</xsl:for-each>
														</tbody>
													</table>
												</td>
											</tr>
										</tbody>
									</table>
								</td>
							</tr>
						</xsl:if>
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
