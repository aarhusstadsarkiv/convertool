<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
  xmlns:m="http://rep.oio.dk/medcom.dk/xml/schemas/2020/03/30/">

  <xsl:output method="html"/>

  <xsl:variable name="newlineGenReport">
    <xsl:text>
   </xsl:text>
  </xsl:variable>

  <!--  GENETICSREPORT -->
  <xsl:template match="m:Emessage[m:GeneticsReport]"> 
    <xsl:for-each select="m:GeneticsReport">
      <td valign="top" width="100%" bgcolor="#ffffff" colspan="2">
        <table width="100%">
          <tbody>
            <tr>
              <xsl:call-template name="ShowMessageHeader">
                <xsl:with-param name="MessageName" select="'Genetiksvar'"/>
              </xsl:call-template>
            </tr>
            <tr>
              <td>
                <table>
                  <tbody>
                    <tr>
                      <td valign="top">
                        <h2>Prøvetagnings information</h2>
                      </td>
                    </tr>
                    
                    
                  <xsl:if
                      test="count(m:RequisitionInformation/m:ClinicalInformation/m:Paragraph) > 0">
                      <tr>
                        <td align="right">
                          <b>Klinisk information:</b>
                        </td>
                        <td>
                          <xsl:apply-templates
                            select="m:RequisitionInformation/m:ClinicalInformation/m:Paragraph"/>
                        </td>
                      </tr>
                    </xsl:if>




                    <tr>
                      <td align="right">
                        <b>Prøve status:</b>
                      </td>
                      <td>
                        <xsl:value-of
                          select="m:LaboratoryResults/m:GeneralResultInformation/m:ReportStatusCode"
                        />
                      </td>
                    </tr>
                    <tr>
                      <td align="right">
                        <b>Status på svar:</b>
                      </td>
                      <td>
                        <xsl:value-of
                          select="m:LaboratoryResults/m:GeneralResultInformation/m:ResultStatusCode"
                        />
                      </td>
                    </tr>
                    <xsl:if
                      test="count(m:LaboratoryResults/m:GeneralResultInformation/m:Summary) > 0">
                      <tr>
                        <td align="right">
                          <b>Resumé:</b>
                        </td>
                        <td>
                          <xsl:value-of
                            select="m:LaboratoryResults/m:GeneralResultInformation/m:Summary"/>
                        </td>
                      </tr>
                    </xsl:if>

                    <xsl:if test="count(m:RequisitionInformation/m:Comments/m:Text/m:Paragraph) > 0">
                      <tr>
                        <td align="right">
                          <b>Bemærkning til rekvisitionen:</b>
                        </td>
                        <tr>
                          <td/>
                          <td>
                            <div style="background-color: #ffffcc; width: 100%; padding: 5px">
                              <xsl:apply-templates
                                select="m:RequisitionInformation/m:Comments/m:Text/m:Paragraph"/>
                            </div>
                          </td>
                        </tr>
                      </tr>
                    </xsl:if>
                    <xsl:if test="count(m:LaboratoryResults/m:Comments) > 0">
                      <tr>
                        <td align="right">
                          <b>Kommentar til prøve resultaterne:</b>
                        </td>
                        <tr>
                          <td/>
                          <td>
                            <xsl:for-each select="m:LaboratoryResults/m:Comments">
                              <xsl:call-template name="codeTypeTableGenReport"/>
                            </xsl:for-each>
                          </td>
                        </tr>
                      </tr>
                    </xsl:if>
                  </tbody>
                </table>
              </td>
            </tr>
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
 
  <xsl:template match="m:Paragraph">
    <xsl:value-of select="."/>
    <br/>
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

      <!-- Investigation erstattes med "Prøve" -->
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
            <br/>
            <tr>
              <td>
                <b>Analyse: </b>
              </td>
              <td align="right">
                <b>
                  <xsl:value-of select="m:TableFormat/m:ResultHeadline"/>
                </b>
              </td>
            </tr>
            <tr>
              <td valign="top">
                <b>Rekvirentens prøvenr.:</b>
              </td>
              <td valign="top">
                <xsl:for-each
                  select="m:LaboratoryResults/m:Result/m:Sample/m:RequesterSampleIdentifier">
                  <xsl:call-template name="FormatDateTime"/>
                </xsl:for-each>
              </td>
            </tr>
            <tr>
              <td valign="top">
                <b>Laboratoriets prøvenr.:</b>
              </td>
              <td valign="top">
                <xsl:for-each
                  select="m:LaboratoryResults/m:Result/m:Sample/m:RequesterSampleIdentifier">
                  <xsl:call-template name="FormatDateTime"/>
                </xsl:for-each>
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
                <b>Svardato:</b>
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
                <b> </b>
              </td>
              <td>
                <b> </b>
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
          </table>
       
       
       
        </xsl:element>
      </xsl:for-each>
    </div>
  </xsl:template>

  <xsl:template name="examnimationTableGenReport">
    <table>
      <br/>
      <tr>
        <td>
          <b>Undersøgelse: </b>
        </td>
        <td align="right">
          <b>
            <xsl:value-of select="m:ExaminationTypeCode"/>
          </b>
        </td>
      </tr>
    </table>
    <br/>
    <br/>
    <table>
      <xsl:attribute name="bordercolor">
        <xsl:value-of select="'black'"/>
      </xsl:attribute>
      <tr>
        <xsl:attribute name="bgcolor">
          <xsl:value-of select="$oddrowbgcolor"/>
        </xsl:attribute>
        <!--   <xsl:value-of select="$evenrowbgcolor"/> -->
        <td>
          <b>
            <u>Beskrivelse</u>
          </b>
        </td>

        <td>
          <b>
            <u>Værdi</u>
          </b>
        </td>
      </tr>
      <tr>
        <xsl:attribute name="bgcolor">
          <xsl:value-of select="$evenrowbgcolor"/>
        </xsl:attribute>
        <td>
          <b>Analyse kode:</b>
        </td>
        <td>
          <xsl:value-of select="m:MICAnalysisCode"/>
        </td>
      </tr>
      <tr>
        <xsl:attribute name="bgcolor">
          <xsl:value-of select="$oddrowbgcolor"/>
        </xsl:attribute>
        <td>
          <b>Analyse type:</b>
        </td>

        <td>
          <xsl:value-of select="m:AnalysisCodeType"/>
        </td>
      </tr>
      <tr>
        <xsl:attribute name="bgcolor">
          <xsl:value-of select="$evenrowbgcolor"/>
        </xsl:attribute>
        <td>
          <b>Analyse ansvarlig:</b>
        </td>
        <td>
          <xsl:value-of select="m:AnalysisCodeResponsible"/>
        </td>
      </tr>
      <tr>
        <xsl:attribute name="bgcolor">
          <xsl:value-of select="$oddrowbgcolor"/>
        </xsl:attribute>
        <td>
          <b>Analyse forkortelse:</b>
        </td>

        <td>
          <xsl:value-of select="m:AnalysisShortName"/>
        </td>
      </tr>
      <tr>
        <xsl:attribute name="bgcolor">
          <xsl:value-of select="$evenrowbgcolor"/>
        </xsl:attribute>
        <td>
          <b>Undersøgelse:</b>
        </td>
        <td>
          <xsl:value-of select="m:AnalysisMDSName/m:Examination"/>
        </td>
      </tr>
      <tr>
        <xsl:attribute name="bgcolor">
          <xsl:value-of select="$oddrowbgcolor"/>
        </xsl:attribute>
        <td>
          <b>Materiale:</b>
        </td>

        <td>
          <xsl:value-of select="m:AnalysisMDSName/m:Material"/>
        </td>
      </tr>
      <tr>
        <xsl:attribute name="bgcolor">
          <xsl:value-of select="$evenrowbgcolor"/>
        </xsl:attribute>
        <td>
          <b>Materialets oprindelsessted:</b>
        </td>
        <td>
          <xsl:value-of select="m:AnalysisMDSName/m:Locationn"/>
        </td>
      </tr>
      <tr>
        <xsl:attribute name="bgcolor">
          <xsl:value-of select="$oddrowbgcolor"/>
        </xsl:attribute>
        <td>
          <b>Yderligere information om materialets placering:</b>
        </td>

        <td>
          <xsl:value-of select="m:SupplementaryLocation"/>
        </td>
      </tr>
      <tr>
        <xsl:attribute name="bgcolor">
          <xsl:value-of select="$evenrowbgcolor"/>
        </xsl:attribute>
        <td>
          <b>Undersøger2:</b>
        </td>
        <td>
          <xsl:value-of select="m:Examinator"/>
        </td>
      </tr>
      <tr>
        <xsl:attribute name="bgcolor">
          <xsl:value-of select="$oddrowbgcolor"/>
        </xsl:attribute>
        <td>
          <b>Udførende laboratorie:</b>
        </td>
        <td>
          <xsl:value-of select="m:ProducerOfLabResult/m:Identifier"/>
        </td>
      </tr>
      <tr>
        <xsl:attribute name="bgcolor">
          <xsl:value-of select="$evenrowbgcolor"/>
        </xsl:attribute>
        <td>
          <b>Laboratorie kode:</b>
        </td>
        <td>
          <xsl:value-of select="m:ProducerOfLabResult/m:IdentifierCode"/>
        </td>
      </tr>
      <tr>
        <xsl:attribute name="bgcolor">
          <xsl:value-of select="$oddrowbgcolor"/>
        </xsl:attribute>
        <td>
          <b>Resultat resumé:</b>
        </td>
        <td>
          <xsl:value-of select="m:Summary"/>
        </td>
      </tr>
    </table>
    <!-- New Line -->
    <table>
      <thead>
        <h4> </h4>
      </thead>
    </table>
  </xsl:template>

  <xsl:template name="analysisFindingsTableGenReport">
    <table width="100%">
      <xsl:attribute name="bordercolor">
        <xsl:value-of select="'black'"/>
      </xsl:attribute>
      <xsl:if test="count(m:Analysis/m:Code) > 0">
        <tr>
          <xsl:attribute name="bgcolor">
            <xsl:value-of select="white"/>
          </xsl:attribute>
          <td width="34%" >
            <b>       </b>
          </td>
          <td width="42%">
            <b>Analyse</b>
          </td>
          <td width="20%">
            <b>Fortolkning</b>
          </td>
        </tr>
        <tr>
          <xsl:attribute name="bgcolor">
            <xsl:value-of select="$evenrowbgcolor"/>
          </xsl:attribute>
          <td>
            <b>Klassifikationsnummer</b>
          </td>
          <td>
            <xsl:value-of select="m:Analysis/m:Code"/>
          </td>
          <td>
            <xsl:value-of select="m:Findings/m:InterPretation/m:Code"/>
          </td>
        </tr>
        <tr>
          <xsl:attribute name="bgcolor">
            <xsl:value-of select="$oddrowbgcolor"/>
          </xsl:attribute>
          <td>
            <b>Klassifikationstype</b>
          </td>
          <td>
            <xsl:value-of select="m:Analysis/m:CodeType"/>
          </td>
          <td>
            <xsl:value-of select="m:Findings/m:InterPretation/m:CodeType"/>
          </td>
        </tr>
        <tr>
          <xsl:attribute name="bgcolor">
            <xsl:value-of select="$evenrowbgcolor"/>
          </xsl:attribute>
          <td>
            <b>Klassifikationsansvarlig:</b>
          </td>
          <td>
            <xsl:value-of select="m:Analysis/m:CodeResponsible"/>
          </td>
          <td>
            <xsl:value-of select="m:Findings/m:InterPretation/m:CodeResponsible"/>
          </td>         
        </tr>
      </xsl:if>
      <xsl:if test="count(m:Analysis/m:Text) > 0">
        <tr>
          <xsl:attribute name="bgcolor">
            <xsl:value-of select="$oddrowbgcolor"/>
          </xsl:attribute>
          <td>
            <b>Klassifikationstekst:</b>
          </td>
          <!-- RUN <td>
            <xsl:value-of select="m:Analysis/m:Text"/>
          </td> -->
          <td>          
            <xsl:for-each select="m:Analysis/m:Text/m:Paragraph">           
              <xsl:call-template name="paragraphListingGenReport"/>
            </xsl:for-each>   
          </td>         
          <td> 
            <xsl:value-of select="m:Findings/m:InterPretation/m:Text"/>
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
  


  <xsl:template name="codeTypeTableGenReport">
    <table>
      <xsl:attribute name="bordercolor">
        <xsl:value-of select="'black'"/>
      </xsl:attribute>
      <xsl:if test="count(m:Code) > 0">
        <tr>
          <xsl:attribute name="bgcolor">
            <xsl:value-of select="$evenrowbgcolor"/>
          </xsl:attribute>
          <td>
            <b>Klassifikationsnummer</b>
          </td>
          <td>
            <xsl:value-of select="m:Code"/>
          </td>
        </tr>
        <tr>
          <xsl:attribute name="bgcolor">
            <xsl:value-of select="$oddrowbgcolor"/>
          </xsl:attribute>
          <td>
            <b>Klassifikationstype</b>
          </td>
          <td>
            <xsl:value-of select="m:CodeType"/>
          </td>
        </tr>
        <tr>
          <xsl:attribute name="bgcolor">
            <xsl:value-of select="$evenrowbgcolor"/>
          </xsl:attribute>
          <td>
            <b>Klassifikationsansvarlig:</b>
          </td>
          <td>
            <xsl:value-of select="m:CodeResponsible"/>
          </td>

        </tr>
      </xsl:if>
      <xsl:if test="count(m:Text) > 0">
        <tr>
          <xsl:attribute name="bgcolor">
            <xsl:value-of select="$oddrowbgcolor"/>
          </xsl:attribute>
          <td>
            <b>Klassifikationstekst:</b>
          </td>
          <td>
            <xsl:value-of select="m:Text"/>
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

  <xsl:template name="codeTypeListingGenReport">

    <!-- New Line -->
    <table>
      <thead>
        <h4> </h4>
      </thead>
    </table>
  </xsl:template>

  <xsl:template name="paragraphListingGenReport">
    <table>
      <tr>
        <td width="100%" >
          <xsl:value-of select="."/> 
        </td>
      </tr>
    </table>
  </xsl:template>



  <!-- Mikroskopi -->
  <xsl:template match="m:MicroscopicFindings">
    <h4>
      <xsl:value-of select="m:Headline"/>
    </h4>

    <!-- bemærkninger til mikroskopi -->
    <table>
      <tr>
        <td align="left">
          <h5> Bemærkninger: </h5>
        </td>
        <td>
          <xsl:for-each select="m:Comments">
            <tr>
              <td> </td>
              <td>
                <div style="background-color: #ffffcc; width: 100%; padding: 5px">
                  <xsl:apply-templates select="m:Paragraph"/>
                </div>
              </td>
            </tr>
          </xsl:for-each>
        </td>
      </tr>
    </table>
    
    <h5> Mikroskopiske fund </h5>
    <xsl:call-template name="microscopicFindingsTableGenReport"/>

    <h5>Grouping</h5>
    <xsl:for-each select="m:Grouping">
      <xsl:call-template name="microscopicCodesTableGenReport"/>
    </xsl:for-each>


    <!-- Original 
      <xsl:for-each select="m:Grouping/m:MicroscopicType">
       <table>
        <tr>
          <td>
            <h5>Type: <xsl:value-of select="m:Type"/></h5>
          </td>
        </tr>
          <xsl:for-each select="m:Details/m:Identification">
            <h5>Identikation</h5>
                <xsl:call-template name="codeTypeTableGenReport"/>
          </xsl:for-each>
        
         <xsl:for-each select="m:Details/m:Value">
              <h5>Værdi</h5>
              <xsl:call-template name="codeTypeTableGenReport" />
         </xsl:for-each>
       </table>
      </xsl:for-each>    
     -->

  </xsl:template>

  <xsl:template name="cultureFindingsTableGenReport">
    <xsl:variable name="nrOfColumns" select="count(./m:Microorganism) + 1"/>
    <h4>
      <xsl:value-of select="./m:Headline"/>
    </h4>
    <table class="culturefindings" width="100%">
      <xsl:attribute name="bordercolor">
        <xsl:value-of select="'black'"/>
      </xsl:attribute>
      <tr>
        <th>Antibiotika</th>
        <xsl:for-each select="m:Microorganism">
          <th>
            <xsl:value-of select="position()"/>
          </th>
        </xsl:for-each>
      </tr>
      <xsl:for-each select="m:Pattern">
        <xsl:variable name="entries" select="m:PatternEntry"/>
        <xsl:for-each select="m:Antibiotic">
          <tr>
            <xsl:attribute name="bgcolor">
              <xsl:choose>
                <xsl:when test="position() mod 2">
                  <xsl:value-of select="$oddrowbgcolor"/>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="$evenrowbgcolor"/>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:attribute>
            <td>
              <xsl:value-of select="./m:AntibioticName/m:Text"/>
            </td>
            <xsl:variable name="abId" select="position()"/>
            <xsl:for-each select="../../m:Microorganism">
              <xsl:variable name="micId" select="position()"/>
              <td>
                <xsl:for-each select="$entries">
                  <xsl:if test="m:RefAntibiotic = $abId">
                    <xsl:if test="m:RefMicroorganism = $micId">
                      <xsl:value-of select="m:Susceptibility"/>
                    </xsl:if>
                  </xsl:if>
                </xsl:for-each>
              </td>
            </xsl:for-each>
          </tr>
        </xsl:for-each>
      </xsl:for-each>
      <tr>
        <xsl:attribute name="bgcolor">
          <xsl:value-of select="white"/>
        </xsl:attribute>
        <td colspan="{$nrOfColumns}">
          <xsl:for-each select="./m:Pattern/m:SusceptibilityInterpretation/m:Paragraph">
            <small>
              <xsl:value-of select="."/>
            </small>
            <br/>
          </xsl:for-each>
        </td>
      </tr>
    </table>
  </xsl:template>

   <xsl:template name="microscopicExaminationTableGenReport">
     <xsl:variable name="nrOfColumns" select="6"/>
     <h4> Dyrkede mikroorganismer </h4>
     <table class="microscopicExamination" width="100%">
       <xsl:attribute name="bordercolor">
         <xsl:value-of select="'black'"/>
       </xsl:attribute>
       <tr>
         <th>Nr</th>
         <th>Vækst</th>
         <th>Navn på Mikroorganisme</th>
         <!--  <th width="25%">Kommentar</th>  -->
         <th>Kode</th>
         <th>Type</th>
         <th>Ansvarlige</th>
       </tr>
       <xsl:for-each select="m:Microorganism">
         <tr>
           <xsl:attribute name="bgcolor">
             <xsl:choose>
               <xsl:when test="position() mod 2">
                 <xsl:value-of select="$oddrowbgcolor"/>
               </xsl:when>
               <xsl:otherwise>
                 <xsl:value-of select="$evenrowbgcolor"/>
               </xsl:otherwise>
             </xsl:choose>
           </xsl:attribute>
           <td>
             <xsl:value-of select="position()"/>
           </td>
           <td>
             <xsl:value-of select="m:GrowthValue/m:Text/m:Paragraph"/>
           </td>
           <td>
             <xsl:value-of select="m:Identification/m:Text/m:Paragraph"/>
           </td>
           <!--     <td>
             <xsl:value-of select="m:SpeciesComment/m:Text/m:Paragraph"/>
           </td>  -->
           <td>
             <xsl:value-of select="m:Identification/m:Code"/>
           </td>
           <td>
             <xsl:value-of select="m:Identification/m:CodeType"/>
           </td>
           <td>
             <xsl:value-of select="m:Identification/m:CodeResponsible"/>
           </td>
         </tr>
       </xsl:for-each>
 
     </table>
     <br/>
   </xsl:template>

  <!-- Tabel til visning af mikroskopiske fund -->
  <xsl:template name="microscopicFindingsTableGenReport">
    <xsl:variable name="nrOfColumns" select="2"/>
    <table class="microscopicFindings2" width="100%">
      <xsl:attribute name="bordercolor">
        <xsl:value-of select="'black'"/>
      </xsl:attribute>
      <tr>
        <th>Værdi</th>
        <th>Identifikation</th>
      </tr>
      <xsl:for-each select="m:Grouping/m:MicroscopicType">
        <tr>
          <xsl:attribute name="bgcolor">
            <xsl:choose>
              <xsl:when test="position() mod 2">
                <xsl:value-of select="$oddrowbgcolor"/>
              </xsl:when>
              <xsl:otherwise>
                <xsl:value-of select="$evenrowbgcolor"/>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:attribute>
          <td>
            <xsl:value-of select="m:Details/m:Value/m:Text/m:Paragraph"/>
          </td>
          <td>
            <xsl:value-of select="m:Details/m:Identification/m:Text/m:Paragraph"/>
          </td>
        </tr>
      </xsl:for-each>
    </table>
    <br/>
  </xsl:template>


<!-- Tabel til visning af koder for mikroskopiske fund -->
  <xsl:template name="microscopicCodesTableGenReport">
    <xsl:variable name="nrOfColumns" select="4"/>
    <h5>
     Gruppenavn: <xsl:value-of select="m:Headline/m:Text/m:Paragraph"/>
    </h5>
    <xsl:for-each select="m:MicroscopicType">
      <h6> 
        Mikroskopitype: <xsl:value-of select="m:Type"/>
      </h6>
      <h6> 
        Identifikation:
      </h6>    
      <table class="microscopicCodesTable3" width="100%">
        <xsl:attribute name="bordercolor">
          <xsl:value-of select="'black'"/>
        </xsl:attribute>
        <tr>
          <th></th>
        </tr>
        <tr>
          <th>Klassifikationsnummer</th>
          <th>Klassifikationstype</th>
          <th>Klassifikationsanvarlig</th>
          <th>Klassifikationstekst</th>
        </tr>
          <tr>
            <xsl:attribute name="bgcolor">
              <xsl:choose>
                <xsl:when test="position() mod 2">
                  <xsl:value-of select="$oddrowbgcolor"/>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="$evenrowbgcolor"/>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:attribute>
            <td>
              <xsl:value-of select="m:Details/m:Identification/m:Code"/>
            </td>
            <td>
              <xsl:value-of select="m:Details/m:Identification/m:CodeType"/>
            </td>
            <td>
              <xsl:value-of select="m:Details/m:Identification/m:CodeResponsible"/>
            </td>
            <td>
              <table>
                <xsl:for-each select="m:Details/m:Identification/m:Text/m:Paragraph">
                  <tr>
                    <td>
                      <xsl:value-of select="current()"/>
                    </td>
                  </tr>
                </xsl:for-each>
              </table>
            </td>
          </tr>
         
      </table>
      <h6> 
        Value:
      </h6>
      <table class="microscopicCodesTable4" width="100%">
        <xsl:attribute name="bordercolor">
          <xsl:value-of select="'black'"/>
        </xsl:attribute>
        <tr>
          <th>Klassifikationsnummer</th>
          <th>Klassifikationstype</th>
          <th>Klassifikationsansvarlig</th>
          <th>Klassifikationstekst</th>
        </tr>
        <tr>
          <xsl:attribute name="bgcolor">
            <xsl:choose>
              <xsl:when test="position() mod 2">
                <xsl:value-of select="$oddrowbgcolor"/>
              </xsl:when>
              <xsl:otherwise>
                <xsl:value-of select="$evenrowbgcolor"/>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:attribute>
          <td>
            <xsl:value-of select="m:Details/m:Value/m:Code"/>
          </td>
          <td>
            <xsl:value-of select="m:Details/m:Value/m:CodeType"/>
          </td>
          <td>
            <xsl:value-of select="m:Details/m:Value/m:CodeResponsible"/>
          </td>
          <td>
            <table>
              <xsl:for-each select="m:Details/m:Value/m:Text/m:Paragraph">
                <tr>
                  <td>
                    <xsl:value-of select="current()"/>
                  </td>
                </tr>
              </xsl:for-each>
            </table>
          </td>
        </tr>    
      </table>
    </xsl:for-each>
  </xsl:template> 
</xsl:stylesheet>
