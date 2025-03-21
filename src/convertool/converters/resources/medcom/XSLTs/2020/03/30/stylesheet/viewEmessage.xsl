<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:m="http://rep.oio.dk/medcom.dk/xml/schemas/2020/03/30/"
	xmlns:cpr="http://rep.oio.dk/cpr.dk/xml/schemas/core/2002/06/28/"
	xmlns:dkcc="http://rep.oio.dk/ebxml/xml/schemas/dkcc/2003/02/13/"
	xmlns:xs="http://www.w3.org/2001/XMLSchema">
	<xsl:output media-type="text/html"/>    
	
	<xsl:include href="WebReport.xsl"/>

	
	
	
	
	<!--
		GENETICS / GENETIK REPORT  
	-->
	<xsl:template match="m:Emessage[m:GeneticsReport]">
		<xsl:for-each select="m:GeneticsReport">
			<td valign="top" width="100%" bgcolor="#ffffff" colspan="2">
				
				<table width="100%">
					<tbody>
						<tr>
							<xsl:call-template name="ShowMessageHeader">
								<xsl:with-param name="MessageName" select="'Klinisk Genetiske svar TEST'"
								/>
							</xsl:call-template>
						</tr>
						<tr>
							<td valign="top" width="100%">
								<xsl:call-template name="LabSchemaTable"/>
								<table>
									<tbody>
										<tr>
											<td valign="top">
												<b> Oplysnigner vedr. samlede rekvisition/svar:  </b>
											</td>
											<td>
												<b> </b>
											</td>
										</tr>
										<tr>
											<td valign="top">
												<b>_______________________________________</b>
											</td>
											<td>
												<b> </b>
											</td>
										</tr>
										<tr>
											<td valign="top">
												<b>Svarstatus:</b>
											</td>
											<td valign="top">
												<xsl:value-of select="m:LaboratoryResults/m:GeneralResultInformation/m:ReportStatusCode"/>										
											</td>
										</tr>
										<tr>
											<td valign="top">
												<b> </b>
											</td>
											<td>
												<b> </b>
											</td>
										</tr>
										<tr>
											<td valign="top">
												<b>Rekvirentens rekvisitionsnr.:</b>
											</td>
											<td valign="top">
												<xsl:value-of select="m:RequisitionInformation/m:RequestersRequisitionIdentifier"/>			
											</td>
										</tr>
										<tr>
										<td valign="top">
											<b>Laboratoriets rekvisitionsnr.:</b>
										</td>
										<td valign="top">
											<xsl:value-of select="m:RequisitionInformation/m:ReceiversRequisitionIdentifier "/>									
										</td>
										</tr>
									
										<tr>
											<td valign="top">
												<b> </b>
											</td>
											<td>
												<b> </b>
											</td>
										</tr>
										<tr>
											<td valign="top">
												<b></b>
											</td>
											<td valign="top">
												<b></b>
												
											</td>
										</tr>
										<tr>
											<td valign="top">
												<b></b>
											</td>
											<td valign="top">
												<b></b>
												
											</td>
										</tr>
										<tr>
											<td valign="top">
												<b>Prøvetagningsdato:</b>
											</td>
											<td valign="top">
												<xsl:for-each
												select="m:RequisitionInformation/m:SamplingDateTime">
												<xsl:call-template name="FormatDateTime"/>
												</xsl:for-each>
											</td>
										</tr>
										<tr>
											<td valign="top">
												<b>Modt. dato:</b>
											</td>
											<td valign="top">
												<xsl:for-each
												select="m:RequisitionInformation/m:SampleReceivedDateTime">
												<xsl:call-template name="FormatDateTime"/>
												</xsl:for-each>
											</td>
										</tr>
										<tr>
											<td valign="top">
												<b>Svardato :</b>
											</td>
											<td valign="top">
												<xsl:for-each
													select="m:LaboratoryResults/m:GeneralResultInformation/m:ResultsDateTime">
													<xsl:call-template name="FormatDateTime"/>
												</xsl:for-each>
											</td>
										</tr>
										<tr>
											<td valign="top">
												<b>Rekvisitionsdato:</b>
											</td>
											<td valign="top">
												<xsl:for-each
													select="m:RequisitionInformation/m:RequisitionDateTime">
													<xsl:call-template name="FormatDateTime"/>
												</xsl:for-each>
											</td>
										</tr>
										<tr>
											<td valign="top">
												<b></b>
											</td>
											<td valign="top">
												<b></b>
												
											</td>
										</tr>
										<tr>
											<td valign="top">
												<b></b>
											</td>
											<td valign="top">
												<b></b>
												
											</td>
										</tr>
										
										<tr>
											<td valign="top">
												<b></b>
											</td>
											<td valign="top">
												<b></b>
												
											</td>
										</tr>
										<tr>
											<td valign="top">
												<b></b>
											</td>
											<td valign="top">
												<b></b>
												
											</td>
										</tr>
										<tr>
											<td valign="top">
												<b>Kliniske oplysninger inkl. indikation:</b>
											</td>
											<td valign="top">
												<xsl:value-of select="m:RequisitionInformation/m:ClinicalInformation"/>
											</td>
										</tr>
										
										<tr>
											<td valign="top">
												<b>Kommentar vedr. samlede svar:</b>
											</td>
											<td valign="top">
												<xsl:value-of select="m:RequisitionInformation/m:Comments"/>										
											</td>
										</tr>
										<tr>
											<td valign="top">
												<b><xsl:value-of select="m:LaboratoryResults/m:GeneralResultInformation/m:Conclusion/m:Headline"/></b>
											</td>
											<td valign="top">
												<xsl:value-of select="m:LaboratoryResults/m:GeneralResultInformation/m:Conclusion/m:Text"/>										
											</td>
										</tr>
										<tr>
											<td valign="top">
												<b> </b>
											</td>
											<td>
												<b> </b>
											</td>
										</tr>
										<tr>
											<td valign="top">
												<b></b>
											</td>
											<td valign="top">
												<b></b>
												
											</td>
										</tr>
										<tr>
											<td valign="top">
												<b></b>
											</td>
											<td valign="top">
												<b></b>
												
											</td>
										</tr>
										
										<tr>
											<td valign="top">
												<b>Laboratoriets interne produktionsID:</b>
											</td>
											<td valign="top">
												<xsl:value-of select="m:LaboratoryResults/m:GeneralResultInformation/m:LaboratoryInternalProductionIdentifier "/>										
											</td>
										</tr>
										<xsl:if test="m:LaboratoryResults/m:GeneralResultInformation/m:ToLabIdentifier">
											<tr>
												<td valign="top">
													<b>Sendeprøve til lab:</b>
												</td>
												<td valign="top">
													<xsl:value-of select="m:LaboratoryResults/m:GeneralResultInformation/m:ToLabIdentifier"/>
												</td>
											</tr>
											<tr>
												<td valign="top">
													<b></b>
												</td>
												<td valign="top">
													<b></b>
													
												</td>
											</tr>
											<tr>
												<td valign="top">
													<b></b>
												</td>
												<td valign="top">
													<b></b>
													
												</td>
											</tr>
											<tr>
												<td valign="top">
													<b></b>
												</td>
												<td valign="top">
													<b></b>
													
												</td>
											</tr>
											
												
										</xsl:if>
										
										
									</tbody>
									</table>



								






									<!-- Tabel til skemavisning 
									<table>
										<tbody>
											<tr>
												<td>
													<b>Prøvedato:</b>
												</td>
												<td valign="top">
														<xsl:for-each
															select="m:RequisitionInformation/m:SamplingDateTime">
															<xsl:call-template name="FormatDateTime"/>
														</xsl:for-each>
												</td>		
											</tr>
											<tr>
												<td>
													<b>Rekvisitionsnummer:</b>
												</td>											
												<td valign="top">
													<xsl:value-of select="m:RequisitionInformation/m:RequestersRequisitionIdentifier"/>													
												</td>												
											</tr>
									
											<tr>
											<td>
												<b>Bemærkning til rekv.</b>
											</td>
												<td valign="top">
													<xsl:value-of select="m:RequisitionInformation/m:Comments"/>													
												</td>	
											</tr>
											<tr>
												<td>
													<b>Type:</b>
												</td>	
												<td valign="top">
													<b>GENETIK</b>
												</td>	
											</tr>
											<xsl:for-each
												select="m:LaboratoryResults/m:Result">
												<tr>
													<td valign="top">
														<xsl:value-of select="m:TableFormat/m:ResultHeadline"/>										
													</td>
													<td valign="top">
														<xsl:value-of select="m:TableFormat/m:TableResult"/>	
													</td>	
												</tr>
											</xsl:for-each>
										</tbody>
									</table>
-->

									<table>
										<tbody>
											<!-- Her starter transformationen af undersøgelses data - LaboratoryResults -->
										<tr>
											<td valign="top" width="100%">
												<table>
													<tbody>
														<tr>
															<td valign="top">
																<script language="javascript" type="text/javascript">
																	var olddivid = 'Investigation1';
																	
																	function hello(link){
																	var oldlink = document.getElementById('current');
																	oldlink.setAttribute('id','val');
																	link.setAttribute('id','current');
																	var divid = link.getAttribute('href');
																	divid = divid.split('?')[1];
																	divid = 'Investigation'+divid;
																	var olddiv = document.getElementById(olddivid);
																	olddiv.setAttribute('class','hidden');
																	olddiv.className = 'hidden';
																	var newdiv = document.getElementById(divid);
																	newdiv.setAttribute('class','visible');
																	newdiv.className = 'visible';
																	olddivid = divid;
																	return false;
																	}
																	
																</script>
																<table>
																	<tbody>
																		<tr>
																			<td colspan="4">
																				<xsl:apply-templates select="m:LaboratoryResults"/>
																			</td>
																		</tr>
																	</tbody>
																</table>
															</td>
														</tr>
													</tbody>
												</table>
											</td>
										</tr>
										
										</tbody>
									</table>
								
							
								<!--
									<table>
										<tbody>
											<tr>
											<td valign="top">
												<b>Tabelsvar:</b>
											</td>
											<td valign="top">
												<xsl:value-of select="m:LaboratoryResults/m:TableFormat/m:TableResult"/>
											</td>
											<xsl:if test="m:LaboratoryResults/m:GeneralResultInformation/m:ToLabIdentifier">
												<td valign="top">
													<xsl:value-of select="m:LaboratoryResults/m:GeneralResultInformation/m:ToLabIdentifier"/>
												</td>	
											</xsl:if>											
											<xsl:call-template name="ShowReqStatusGenReport"/>
											<td valign="top">
												<b>Prøvestatus:</b>
											</td>
											<td valign="top">
												<xsl:variable name="RSC" select="m:LaboratoryResults/m:GeneralResultInformation/m:ResultStatusCode"/>
												<xsl:choose>
													<xsl:when test="$RSC='svar_endeligt'">Endeligt svar</xsl:when>
													<xsl:when test="$RSC='svar_midlertidigt'">Foreløbigt svar</xsl:when>
													<xsl:when test="$RSC='svar_rettet'">Rettet svar</xsl:when>
													<xsl:when test="$RSC='proeve_modtaget'">Prøve modtaget</xsl:when>
												</xsl:choose>
											</td>
											<td valign="top">
												<xsl:for-each
													select="m:LaboratoryResults/m:GeneralResultInformation/m:ResultsDateTime">
													<xsl:call-template name="FormatDateTime"/>
												</xsl:for-each>
											</td>
										</tr>
									</tbody>
								</table>
								
								-->
							</td>
						</tr>

						<xsl:if test="m:LaboratoryResults/m:TableFormat/m:AnalysisCode">
							<tr>
								<td valign="top" width="100%">
									<table>
										<tbody>
											<tr>
												<td valign="top">
													<b>NPU-analysekode:</b>
												</td>
												<td valign="top">
													<xsl:value-of select="m:LaboratoryResults/m:TableFormat/m:AnalysisCode"/>
												</td>	
												<td valign="top">
													<b>Analysenavn:</b>
												</td>
												<td valign="top">
													<xsl:value-of select="m:LaboratoryResults/m:TableFormat/m:AnalysisCompleteName"/>
												</td>	
												<td valign="top">
													<b>Kortnavn:</b>
												</td>
												<td valign="top">
													<xsl:value-of select="m:LaboratoryResults/m:TableFormat/m:ResultHeadline"/>
												</td>
											</tr>
										</tbody>
									</table>
								</td>
							</tr>
						</xsl:if>											

						
						
						<xsl:for-each select="m:LaboratoryResults/m:CodedFormat">
							<tr>
								<td valign="top" width="100%">
									<table>
										<tbody>
											<tr>
												<td valign="top">
												<table>
												<tbody>
												<xsl:for-each select="m:Sample">
												<tr>
												<td valign="top">
												<table>
												<tbody>
												<tr>
												<td valign="top">
												<b>Materiale:</b>
												</td>
												<td valign="top">
												<xsl:value-of select="m:MaterialDescription"/>
												</td>
												<td>
												<b>Rekvirentens ID:</b>
												</td>
												<td>
												<xsl:value-of select="m:RequesterSampleIdentifier"
												/>
												</td>
												<td>
												<b>Laboratoriets ID:</b>
												</td>
												<td>
												<xsl:value-of
												select="m:LaboratoryInternalSampleIdentifier"/>
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
						</xsl:for-each>
						<!--
						<xsl:if test="count(m:RequisitionInformation/m:ClinicalInformation)>0">
							<tr>
								<td valign="top" width="100%">
									<table>
										<tbody>
											<tr>
												<td valign="top">
												<b>
														Kliniske oplysninger, indikation
													</b>
												</td>
											</tr>
											<tr>
												<td valign="top">
												<table>
												<tbody>
												<xsl:for-each
												select="m:RequisitionInformation/m:ClinicalInformation">
												<tr>
												<td valign="top">
												<xsl:apply-templates/>
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
-->
						<xsl:for-each select="m:LaboratoryResults/m:TextualFormat/m:InternalReference">
							<tr>
								<td valign="top" width="100%">
									<table>
										<tbody>
											<tr>
												<td valign="top">
													<b>
														<xsl:value-of select="m:Headline"/>
													</b>
												</td>
											</tr>
											<tr>
												<td valign="top">
													<table>
														<tbody>
															<tr>
																<td valign="top">
																	<xsl:apply-templates
																		select="m:Text/text()|m:Text/*"/>
																</td>
															</tr>
														</tbody>
													</table>
												</td>
											</tr>
										</tbody>
									</table>
								</td>
							</tr>
						</xsl:for-each>
						<xsl:for-each select="m:LaboratoryResults/m:TextualFormat/m:GenomeReference">
							<tr>
								<td valign="top" width="100%">
									<table>
										<tbody>
											<tr>
												<td valign="top">
													<b>
														<xsl:value-of select="m:Headline"/>
													</b>
												</td>
											</tr>
											<tr>
												<td valign="top">
													<table>
														<tbody>
															<tr>
																<td valign="top">
																	<xsl:apply-templates
																		select="m:Text/text()|m:Text/*"/>
																</td>
															</tr>
														</tbody>
													</table>
												</td>
											</tr>
										</tbody>
									</table>
								</td>
							</tr>
						</xsl:for-each>
						
						<xsl:for-each select="m:LaboratoryResults/m:TextualFormat/m:AnalysisMethod">
							<tr>
								<td valign="top" width="100%">
									<table>
										<tbody>
											<tr>
												<td valign="top">
												<b>
												<xsl:value-of select="m:Headline"/>
												</b>
												</td>
											</tr>
											<tr>
												<td valign="top">
												<table>
												<tbody>
												<tr>
												<td valign="top">
												<xsl:apply-templates
												select="m:Text/text()|m:Text/*"/>
												</td>
												</tr>
												</tbody>
												</table>
												</td>
											</tr>
										</tbody>
									</table>
								</td>
							</tr>
						</xsl:for-each>
						<xsl:for-each select="m:LaboratoryResults/m:TextualFormat/m:AnalysisResults">
							<tr>
								<td valign="top" width="100%">
									<table>
										<tbody>
											<tr>
												<td valign="top">
												<b>
												<xsl:value-of select="m:Headline"/>
												</b>
												</td>
											</tr>
											<tr>
												<td valign="top">
												<table>
												<tbody>
												<tr>
												<td valign="top">
												<xsl:apply-templates
												select="m:Text/text()|m:Text/*"/>
												</td>
												</tr>
												</tbody>
												</table>
												</td>
											</tr>
											<tr>
												<td>
													<xsl:text>Producent: </xsl:text>
													<xsl:value-of select="m:ProducerOfLabResult/m:IdentifierCode"/>
													<xsl:value-of select="m:ProducerOfLabResult/m:Identifier"/>
												</td>
											</tr>
										</tbody>
									</table>
								</td>
							</tr>
						</xsl:for-each>
						<xsl:for-each select="m:LaboratoryResults/m:TextualFormat/m:Conclusion">
							<tr>
								<td valign="top" width="100%">
									<table>
										<tbody>
											<tr>
												<td valign="top">
												<b>
												<xsl:value-of select="m:Headline"/>
												</b>
												</td>
											</tr>
											<tr>
												<td valign="top">
												<table>
												<tbody>
												<tr>
												<td valign="top">
												<xsl:apply-templates
												select="m:Text/text()|m:Text/*"/>
												</td>
												</tr>
												</tbody>
												</table>
												</td>
											</tr>
										</tbody>
									</table>
								</td>
							</tr>
						</xsl:for-each>
						
						<xsl:for-each select="m:LaboratoryResults/m:TextualFormat/m:Comments">
							<tr>
								<td valign="top" width="100%">
									<table>
										<tbody>
											<tr>
												<td valign="top">
												<b>
												<xsl:value-of select="m:Headline"/>
												</b>
												</td>
											</tr>
											<tr>
												<td valign="top">
												<table>
												<tbody>
												<tr>
												<td valign="top">
												<xsl:apply-templates
												select="m:Text/text()|m:Text/*"/>
												</td>
												</tr>
												</tbody>
												</table>
												</td>
											</tr>
										</tbody>
									</table>
								</td>
							</tr>
						</xsl:for-each>
						<tr>
							<xsl:call-template name="ShowPatientGenReport"/>
						</tr>
						<tr>
							<xsl:call-template name="ShowParticipants"/>
						</tr>
					</tbody>
				</table>
			</td>
		</xsl:for-each>
	</xsl:template>


	<xsl:template name="LabSchemaTable">
		
		
		
		<table width="100%">
			<xsl:attribute name="bordercolor">
				<xsl:value-of select="'black'"/>
			</xsl:attribute>
				<tr>
					<xsl:attribute name="bgcolor">
						<xsl:value-of select="white"/>
					</xsl:attribute>
					<td width="40%" >
						<b> Laboratorieskema </b>
					</td>
					<td width="60%">
						
					</td>
				</tr>
				<tr>
					<td>
						<b>_</b>
					</td>			
				</tr>
				<tr>
					<xsl:attribute name="bgcolor">
						<xsl:value-of select="white"/>
					</xsl:attribute>
					<td width="40%" >
						Prøvedato:
					</td>
					<td width="60%">
						<xsl:for-each
							select="m:RequisitionInformation/m:SamplingDateTime">
							<xsl:call-template name="FormatDateTime"/>
						</xsl:for-each>
					</td>
				</tr>
				<tr>
					<td>
						Rekvisitionsnummer:
					</td>											
					<td valign="top">
						<xsl:value-of select="m:RequisitionInformation/m:RequestersRequisitionIdentifier"/>													
					</td>												
				</tr>				
				<tr>
					<td>
						Bemærkning til rekv.
					</td>
					<td valign="top">
						<xsl:value-of select="m:RequisitionInformation/m:Comments"/>													
					</td>	
				</tr>
				<tr>
					<td>
						<b>Type:</b>
					</td>	
					<td valign="top">
						<b>GENETIK</b>
					</td>	
				</tr>
				<tr>
					<td>
						<b>_</b>
					</td>			
				</tr>
			
				<xsl:for-each
					select="m:LaboratoryResults/m:Result">
					<tr>
						<td valign="top">
							
							<xsl:value-of select="m:TableFormat/m:ResultHeadline"/>
							
						</td>
						<td valign="top">
							
								<xsl:value-of select="m:TableFormat/m:TableResult"/>
															
						</td>	
					</tr>
				</xsl:for-each>
				
				
				
		</table>
		<!-- New Line -->
		<table>
			<thead>
				<h4> </h4>
			</thead>
		</table>
	</xsl:template>
	
	

	<xsl:template match="m:LaboratoryResults">
		<div id="navcontainer">
			<ul id="navlist">
				<xsl:for-each select="m:Result">
					<xsl:element name="li">
						<xsl:if test="position() = 1">
							<xsl:attribute name="id">
								<xsl:value-of select="'active'"/>
							</xsl:attribute>
						</xsl:if>
						<xsl:element name="a">
							<xsl:attribute name="href">#?<xsl:value-of select="position()"/></xsl:attribute>
							<xsl:attribute name="onClick">hello(this);</xsl:attribute>
							<xsl:if test="position() = 1">
								<xsl:attribute name="id">
									<xsl:value-of select="'current'"/>
								</xsl:attribute>
							</xsl:if> Analyse <xsl:value-of select="position()"/>
						</xsl:element>
					</xsl:element>
				</xsl:for-each>
			</ul>
			
			<!-- Result erstattes med "Analyse" -->
			<xsl:for-each select="m:Result">
				<xsl:element name="div">
					<xsl:attribute name="id">Investigation<xsl:value-of select="position()"/></xsl:attribute>
					<xsl:attribute name="class">
						<xsl:choose>
							<xsl:when test="position() = 1">visible</xsl:when>
							<xsl:otherwise>hidden</xsl:otherwise>
						</xsl:choose>
					</xsl:attribute>
					
					<table>
						<tbody>
						
							
							<tr>	
								<td valign="top">
									<table>
										<tbody>
											<tr>
												<td valign="top">
													<xsl:call-template name="AnalysisCodeTable"/>
												</td>
												<td valign="top" >
													<xsl:call-template name="SampleIdTable"/>
													<xsl:call-template name="ProducerOfLabResultTable"/>
													<xsl:call-template name="SampleMaterialTable"/>
												</td>
											</tr>
										</tbody>
									</table>			
								</td>					
							</tr>
						</tbody>
					</table>
					
					<xsl:call-template name="ShowAnalysisResults"/>
					
					
					
					<!--
					<xsl:for-each select="m:Analysis">
						<xsl:call-template name="SimpleTable"/>
					</xsl:for-each>
					-->
					
					
					
					
			
				</xsl:element>
			</xsl:for-each>
		</div>
	</xsl:template>


	
	
	
	
	<xsl:template name="SampleIdTable">
		<table>
			<tbody>
				<tr>
					<td valign="top">
						<b>Rekvirentens prøvenr.:</b>
					</td>
					<td valign="top">
						<xsl:value-of select="m:Sample/m:RequesterSampleIdentifier"/>
					</td>
				</tr>
				<tr>
					<td valign="top">
						<b>Laboratoriets prøvenr.:</b>
					</td>
					<td valign="top">
						<xsl:value-of select="m:Sample/m:LaboratoryInternalSampleIdentifier"/>
					</td>
				</tr>	
			</tbody>
		</table>
	</xsl:template>
	
	<xsl:template name="AnalysisCodeTable">
		<table>
			<tr>
				<td width="30%" >
					
				</td>
				<td valign="right">
					<table>
						<xsl:if test="m:Analysis/m:AnalysisCode">
							<tr>
								<td valign="top" width="100%">
									<table>
										<tbody>
											<tr>
												<tr>	
													<td valign="top">
														<b>Analysekode:</b>
													</td>
													<td valign="top">
														<xsl:value-of select="m:Analysis/m:AnalysisCode"/>
													</td>
												</tr>	
												<td valign="top">
													<b>Kodetype:</b>
												</td>
												<td valign="top">
													<xsl:value-of select="m:Analysis/m:AnalysisCodeType"/>
												</td>
												<tr>
													<td valign="top">
														<b>Kodeansvarlig:</b>
													</td>
													<td valign="top">
														<xsl:value-of select="m:Analysis/m:AnalysisCodeResponsible"/>
													</td>	
												</tr>
												<tr>
													<td valign="top">
														<b>Analysenavn (komplet):</b>
													</td>
													<td valign="top">
														<xsl:value-of select="m:Analysis/m:AnalysisCompleteName"/>
													</td>
												</tr>
												<tr>
													<td valign="top">
														<b>Kortnavn:</b>
													</td>
													<td valign="top">
														<xsl:value-of select="m:Analysis/m:AnalysisShortName"/>
													</td>
												</tr>
												
											</tr>
										</tbody>
									</table>
								</td>
							</tr>
						</xsl:if>
					</table></td>
				
			</tr>
		</table>
		<!-- New Line -->
		<table>
			<thead>
				<h4> </h4>
			</thead>
		</table>
	</xsl:template>
	
	<xsl:template name="ProducerOfLabResultTable">
		<table>
			<xsl:if test="m:ProducerOfLabResult">
				<tr>
					<td valign="top" width="100%">
						<table>
							<tbody>
								<tr>
									<tr>	
										<td valign="top">
											<b>Laboratorie:</b>
										</td>
										<td valign="top">
											<xsl:value-of select="m:ProducerOfLabResult/m:Identifier"/>
										</td>
									</tr>	
									<td valign="top">
										<b>Producentkode:</b>
									</td>
									<td valign="top">
										<xsl:value-of select="m:ProducerOfLabResult/m:IdentifierCode"/>
									</td>							
								</tr>
							</tbody>
						</table>
					</td>
				</tr>
			</xsl:if>
		</table>
	</xsl:template>
	<xsl:template name="SampleMaterialTable">
		<table>
			<xsl:if test="m:Sample">
				<tr>
					<td valign="top" width="100%">
						<table>
							<tbody>
								<tr>
									<tr>	
										<td valign="top">
											<b>Materialetype:</b>
										</td>
										<td valign="top">
											<xsl:value-of select="m:Sample/m:SampleMaterialType"/>
										</td>
									</tr>	
									<td valign="top">
										<b>Materialebeskrivelse:</b>
									</td>
									<td valign="top">
										<xsl:value-of select="m:Sample/m:SampleMaterial"/>
									</td>							
								</tr>
							</tbody>
						</table>
					</td>
				</tr>
			</xsl:if>
		</table>
		<!-- New Line -->
		<table>
			<thead>
				<h4> </h4>
			</thead>
		</table>
	</xsl:template>
	
	
	<xsl:template name="ShowAnalysisResults">
		<table>
			<xsl:for-each select="m:AnalysisResults">
				<tr>
					<td valign="top" width="100%">
						<table>
							<tbody>
								<tr>
									<td valign="top">
										<b>
											<xsl:value-of select="m:Headline"/>
										</b>
									</td>
								</tr>
								<tr>
									<td valign="top">
										<table>
											<tbody>
												<tr>
													<td valign="top">
														<xsl:apply-templates
															select="m:Text/text()|m:Text/*"/>
													</td>
												</tr>
											</tbody>
										</table>
									</td>
								</tr>
							</tbody>
						</table>
					</td>
				</tr>
			</xsl:for-each>
			<xsl:for-each select="m:AnalysisConclusion">
				<tr>
					<td valign="top" width="100%">
						<table>
							<tbody>
								<tr>
									<td valign="top">
										<b>
											<xsl:value-of select="m:Headline"/>
										</b>
									</td>
								</tr>
								<tr>
									<td valign="top">
										<table>
											<tbody>
												<tr>
													<td valign="top">
														<xsl:apply-templates
															select="m:Text/text()|m:Text/*"/>
													</td>
												</tr>
											</tbody>
										</table>
									</td>
								</tr>
							</tbody>
						</table>
					</td>
				</tr>
			</xsl:for-each>
			
	
			
			<xsl:if test="m:Examinator">
			<tr>
				<td valign="top">
					<b>
						Undersøgere:
					</b>
				</td>
			</tr>
			<xsl:for-each select="m:Examinator">
				<tr>
					<td valign="top" width="100%">
						<table>
							<tbody>
								<tr>
									<td>
										<xsl:value-of select="m:PersonName"/>
									</td>
									<td>,</td>
									<td>
										<xsl:value-of select="m:PersonInitials"/>
									</td>
									<td>,</td>
									<td>
										<xsl:value-of select="m:PersonTitle"/>
									</td>									
								</tr>
							</tbody>
						</table>
					</td>
				</tr>
			</xsl:for-each>		
			</xsl:if>
			
			<xsl:for-each select="m:AnalysisMethod">
				<tr>
					<td valign="top" width="100%">
						<table>
							<tbody>
								<tr>
									<td valign="top">
										<b>
											<xsl:value-of select="m:Headline"/>
										</b>
									</td>
								</tr>
								<tr>
									<td valign="top">
										<table>
											<tbody>
												<tr>
													<td valign="top">
														<xsl:apply-templates
															select="m:Text/text()|m:Text/*"/>
													</td>
												</tr>
											</tbody>
										</table>
									</td>
								</tr>
							</tbody>
						</table>
					</td>
				</tr>
			</xsl:for-each>
			<xsl:for-each select="m:Comments">
				<tr>
					<td valign="top" width="100%">
						<table>
							<tbody>
								<tr>
									<td valign="top">
										<b>
											<xsl:value-of select="m:Headline"/>
										</b>
									</td>
								</tr>
								<tr>
									<td valign="top">
										<table>
											<tbody>
												<tr>
													<td valign="top">
														<xsl:apply-templates
															select="m:Text/text()|m:Text/*"/>
													</td>
												</tr>
											</tbody>
										</table>
									</td>
								</tr>
							</tbody>
						</table>
					</td>
				</tr>
			</xsl:for-each>
			<xsl:for-each select="m:InternalReference">
				<tr>
					<td valign="top" width="100%">
						<table>
							<tbody>
								<tr>
									<td valign="top">
										<b>
											<xsl:value-of select="m:Headline"/>
										</b>
									</td>
								</tr>
								<tr>
									<td valign="top">
										<table>
											<tbody>
												<tr>
													<td valign="top">
														<xsl:apply-templates
															select="m:Text/text()|m:Text/*"/>
													</td>
												</tr>
											</tbody>
										</table>
									</td>
								</tr>
							</tbody>
						</table>
					</td>
				</tr>
			</xsl:for-each>
			<xsl:for-each select="m:GenomeReference">
				<tr>
					<td valign="top" width="100%">
						<table>
							<tbody>
								<tr>
									<td valign="top">
										<b>
											<xsl:value-of select="m:Headline"/>
										</b>
									</td>
								</tr>
								<tr>
									<td valign="top">
										<table>
											<tbody>
												<tr>
													<td valign="top">
														<xsl:apply-templates
															select="m:Text/text()|m:Text/*"/>
													</td>
												</tr>
											</tbody>
										</table>
									</td>
								</tr>
							</tbody>
						</table>
					</td>
				</tr>
			</xsl:for-each>
		</table>
		<!-- New Line -->
		<table>
			<thead>
				<h4> </h4>
			</thead>
		</table>
	</xsl:template>
	
	
	
	
	

	<xsl:template name="ShowReqStatusGenReport">
		<td valign="top">
			<b>Status:</b>
		</td>
		<td valign="top">
			<xsl:variable name="RS" select="m:LaboratoryResults/m:GeneralResultInformation/m:ReportStatusCode"/>
			<table border="0">
				<tbody>
					<tr>
						<xsl:choose>
							<xsl:when test="$RS='komplet_svar'">
								<td valign="top">Komplet svar</td>
								<td><img src="img/Ikon_Komplet.PNG"></img></td>
							</xsl:when>
							<xsl:when test="$RS='del_svar'">
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
	<xsl:template name="ShowPatientGenReport">
		<xsl:param name="MedComLetter" select="."/>
		<td valign="top" class="footer">
			<table>
				<tr>
					<td width="50%" valign="top">
						<b>Patient</b>
					</td>
				</tr>
				<tr>
					<td class="frame">
						<div>
							<table>
								<xsl:for-each select="$MedComLetter/*[local-name(.)='Patient']">
									<xsl:call-template name="ShowPerson"/>
								</xsl:for-each>
							</table>
						</div>
					</td>
				</tr>				
			</table>
		</td>
	</xsl:template>


</xsl:stylesheet>
