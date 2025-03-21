<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:m="http://rep.oio.dk/medcom.dk/xml/schemas/2021/06/27/"
  xmlns:gepj="http://medinfo.dk/epj/proj/gepka/20030701/xml/schema"
  xmlns:cpr="http://rep.oio.dk/cpr.dk/xml/schemas/core/2002/06/28/"
  xmlns:dkcc="http://rep.oio.dk/ebxml/xml/schemas/dkcc/2003/02/13/"
  xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xsl:output media-type="text/html"/>

  <!-- template til at vise en fodterapeuthenvisning.  -->
  <xsl:template match="m:Emessage[m:PodiatryReferral]">
    <xsl:for-each select="m:PodiatryReferral">
      <td valign="top" width="100%" bgcolor="#ffffff" colspan="2">
        <table width="100%">
          <tbody>
            <tr>
              <xsl:call-template name="ShowMessageHeader">
                <xsl:with-param name="MessageName" select="'Fodterapihenvisning'"/>
              </xsl:call-template>
            </tr>
            <tr>
              <td valign="top" width="100%">
                <table>
                  <tbody>
                    <tr>
                      <xsl:for-each select="m:AdditionalInformation/m:Priority">
                        <td valign="top">
                          <b>Prioritet:</b>
                        </td>
                        <td valign="top">
                          <xsl:value-of select="."/>
                        </td>
                      </xsl:for-each>
                      <xsl:for-each select="m:AdditionalInformation/m:ReferralStatus">
                        <td valign="top">
                          <b>Behandlingssted:</b>
                        </td>
                        <td valign="top">
                          <xsl:value-of select="."/>
                        </td>
                      </xsl:for-each>
                      <xsl:for-each select="m:AdditionalInformation/m:Transport">
                        <td valign="top">
                          <b>Transport:</b>
                        </td>
                        <td valign="top">
                          <xsl:value-of select="."/>
                        </td>
                      </xsl:for-each>
                      <xsl:for-each select="m:AdditionalInformation/m:Supplementary">
                        <td valign="top">
                          <b>Andet:</b>
                        </td>
                        <td valign="top">
                          <xsl:apply-templates/>
                        </td>
                      </xsl:for-each>
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
                          <b> Henvisnings diagnoser </b>
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
                                    <xsl:value-of select="m:DiagnoseDescriptionCode"/>: </td>
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
                        <b> Kliniske oplysninger </b>
                      </td>
                    </tr>
                    <tr>
                      <xsl:attribute name="bgcolor">
                        <xsl:value-of select="$compoundbgcolor"/>
                      </xsl:attribute>
                      <td valign="top" width="100%">
                        <table width="100%">
                          <tbody>
                            <xsl:for-each select="m:RelevantClinicalInformation/m:Cave">
                              <tr>
                                <td>
                                  <b>Cave</b>
                                </td>
                              </tr>
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
                            <xsl:for-each select="m:RelevantClinicalInformation/m:Anamnesis">
                              <tr>
                                <td>
                                  <b>Anamnese</b>
                                </td>
                              </tr>
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
                              <tr>
                              </tr>
                            </xsl:for-each>

                            
                            <xsl:for-each select="m:RelevantClinicalInformation/m:DiabetesDebut">
                              <tr>
                                <td valign="top">
                                  <b>Diabetes debutår:     </b> <xsl:apply-templates/>
                                </td>
                              </tr>
                            </xsl:for-each>
                            
                            <xsl:for-each select="m:RelevantClinicalInformation/m:DiabeticRetinopathy">
                              <tr>
                                <td valign="top">
                                  <b>Diabetisk øjensygdom:    </b>  <xsl:apply-templates/>
                                </td>
                              </tr>
                            </xsl:for-each>
                            
                            <xsl:for-each select="m:RelevantClinicalInformation/m:DiabeticNephropathy">
                              <tr>
                                <td valign="top">
                                  <b>Diabetisk nyresygdom:   </b> <xsl:apply-templates/>
                                </td>
                              </tr>
                            </xsl:for-each>
                            
                            <xsl:for-each select="m:RelevantClinicalInformation/m:DiabeticBloodPressure">
                              <tr>
                                <td valign="top">
                                  <b>Diabetisk blodtryksmåling på tåniveau:  </b>  <xsl:apply-templates/>
                                </td>
                              </tr>
                            </xsl:for-each>
                            
                            
                            <xsl:for-each select="m:RelevantClinicalInformation/m:Examination">
                              <tr>
                                <td>
                                  <b>Undersøgelser/behandlinger</b>
                                </td>
                              </tr>
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
                            <xsl:for-each select="m:RelevantClinicalInformation/m:ActualMedicine">
                              <tr>
                                <td>
                                  <b>Aktuel medicin</b>
                                </td>
                              </tr>
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
            <xsl:if test="count(m:HospitalVisitation)>0">
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
                              <xsl:for-each select="m:HospitalVisitation">
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
  
  <!-- Clinical Email -->
  <xsl:template match="m:Emessage[m:ClinicalEmail]">
    <xsl:for-each select="m:ClinicalEmail">
      <td valign="top" width="100%" bgcolor="#ffffff" colspan="2">
        <table width="100%">
          <tbody>
            <tr>
              <xsl:call-template name="ShowMessageHeader">
                <xsl:with-param name="MessageName" select="'Korrespondance'"/>
              </xsl:call-template>
            </tr>
            <tr>
              <td valign="top" width="100%">
                <table>
                  <tbody>
                    <tr>
                      <td valign="top">
                        <table>
                          <tbody>
                            <xsl:for-each select="m:AdditionalInformation">
                              <tr>
                                <td valign="top">
                                  <b>Emne: </b>
                                </td>
                                <td valign="top">
                                  <xsl:value-of select="./m:Subject"/>
                                </td>
                                <td> </td>
                                <td valign="top">
                                  <b> Prioritet: </b>
                                </td>
                                <td valign="top">
                                  <xsl:value-of select="m:Priority"/>
                                </td>
                              </tr>
                            </xsl:for-each>
                          </tbody>
                        </table>
                      </td>
                    </tr>
                    <tr>
                      <td valign="top">
                        <b> Brevtekst </b>
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
  
  
  <!-- Speciallæge henvinsing -->
  <xsl:template match="m:Emessage[m:PrivateSpecialistReferral]">
    <xsl:for-each select="m:PrivateSpecialistReferral">
      <td valign="top" width="100%" bgcolor="#ffffff" colspan="2">
        <table width="100%">
          <tbody>
            <tr>
              <xsl:call-template name="ShowMessageHeader">
                <xsl:with-param name="MessageName" select="'Speciallægehenvisning'"/>
              </xsl:call-template>
            </tr>
            <xsl:if test="count(m:Referral)>0">
              <tr>
                <td valign="top" width="100%">
                  <table>
                    <tbody>
                      <tr>
                        <td valign="top">
                          <b> Henvisnings diagnoser </b>
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
                              <!--
                              <xsl:for-each select="m:Referral/m:ReferralAdditional">
                                <tr>
                                  <td valign="top">
                                    <xsl:value-of select="m:DiagnoseDescriptionCode"/>: </td>
                                  <td valign="top">
                                    <xsl:value-of select="m:DiagnoseCode"/>
                                  </td>
                                  <td valign="top">
                                    <xsl:value-of select="m:DiagnoseText"/>
                                  </td>
                                </tr>
                              </xsl:for-each>
                              -->
                            </tbody>
                          </table>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </td>
              </tr>
            </xsl:if>
            <xsl:if test="count(m:AdditionalInformation/m:ClinicalReason)">
              <tr>
                <td valign="top" width="100%">
                  <table>
                    <tbody>
                      <tr>
                        <td valign="top">
                          <b> Henvist speciale </b>
                        </td>
                      </tr>
                      <tr>
                        <td valign="top">
                          <xsl:attribute name="bgcolor">
                            <xsl:value-of select="$highlightbgcolor"/>
                          </xsl:attribute>
                          <table>
                            <tbody>
                              <xsl:for-each select="m:AdditionalInformation/m:ClinicalReason">
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
            <tr>
              <td valign="top" width="100%">
                <table width="100%">
                  <tbody>
                    <tr>
                      <td valign="top" width="100%">
                        <b> Kliniske oplysninger </b>
                      </td>
                    </tr>
                    <tr>
                      <xsl:attribute name="bgcolor">
                        <xsl:value-of select="$compoundbgcolor"/>
                      </xsl:attribute>
                      <td valign="top" width="100%">
                        <table width="100%">
                          <tbody>
                            <xsl:for-each select="m:RelevantClinicalInformation/m:Cave">
                              <tr>
                                <td>
                                  <b>Cave</b>
                                </td>
                              </tr>
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
                            <xsl:for-each select="m:RelevantClinicalInformation/m:Anamnesis">
                              <tr>
                                <td>
                                  <b>Anamnese</b>
                                </td>
                              </tr>
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
                            <xsl:for-each select="m:RelevantClinicalInformation/m:Examination">
                              <tr>
                                <td>
                                  <b>Undersøgelser/behandlinger</b>
                                </td>
                              </tr>
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
                            <xsl:for-each select="m:RelevantClinicalInformation/m:ActualMedicine">
                              <tr>
                                <td>
                                  <b>Aktuel medicin</b>
                                </td>
                              </tr>
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
            <xsl:if test="count(m:HospitalVisitation)>0">
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
                              <xsl:for-each select="m:HospitalVisitation">
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
