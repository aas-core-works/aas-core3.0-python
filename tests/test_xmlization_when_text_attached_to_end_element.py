"""Test the edge cases with the ElementTree parser."""

# pylint: disable=missing-docstring
import io
import unittest
import xml.etree.ElementTree
from typing import Tuple, Iterator

import aas_core3.xmlization as aas_xmlization


class TestTextAttachedToAnEndElement(unittest.TestCase):
    """
    Test the edge case when the ElementTree attaches the text to the end element.

    The quirky part is that the text is *sometimes* attached to the start element
    and *other times* to the end element. We could not figure out which situation
    occurs when.

    Please see also the note in the Python documentation:
    https://docs.python.org/3/library/xml.etree.elementtree.html#xml.etree.ElementTree.XMLPullParser.read_events
    """

    def test_on_a_large_file(self) -> None:
        # Please see:
        # https://github.com/aas-core-works/aas-core3.0-python/issues/17
        # and
        # https://github.com/aas-core-works/aas-core-codegen/pull/443
        text = """\
<environment xmlns="https://admin-shell.io/aas/3/0">
  <assetAdministrationShells>
    <assetAdministrationShell>
      <idShort>NameplateTemplateTestShell</idShort>
      <id>AssetAdministrationShell</id>
      <assetInformation>
        <assetKind>NotApplicable</assetKind>
      </assetInformation>
      <submodels>
        <reference>
          <type>ModelReference</type>
          <keys>
            <key>
              <type>Submodel</type>
              <value>www.example.com/ids/sm/1225_9020_5022_1974</value>
            </key>
          </keys>
        </reference>
      </submodels>
    </assetAdministrationShell>
  </assetAdministrationShells>
  <submodels>
    <submodel>
      <idShort>Nameplate</idShort>
      <description>
        <langStringTextType>
          <language>en</language>
          <text>Contains the nameplate information attached to the product</text>
        </langStringTextType>
      </description>
      <id>www.example.com/ids/sm/1225_9020_5022_1974</id>
      <kind>Template</kind>
      <semanticId>
        <type>ExternalReference</type>
        <keys>
          <key>
            <type>ConceptDescription</type>
            <value>https://admin-shell.io/zvei/nameplate/2/0/Nameplate</value>
          </key>
        </keys>
      </semanticId>
      <submodelElements>
        <file>
          <idShort>CompanyLogo</idShort>
          <semanticId>
            <type>ExternalReference</type>
            <keys>
              <key>
                <type>GlobalReference</type>
                <value>https://admin-shell.io/zvei/nameplate/2/0/Nameplate/CompanyLogo</value>
              </key>
            </keys>
          </semanticId>
          <qualifiers>
            <qualifier>
              <type>Multiplicity</type>
              <valueType>xs:string</valueType>
              <value>ZeroToOne</value>
            </qualifier>
          </qualifiers>
          <value></value>
          <contentType></contentType>
        </file>
        <submodelElementList>
          <idShort>Markings</idShort>
          <description>
            <langStringTextType>
              <language>en</language>
              <text>Note: CE marking is declared as mandatory according to EU Machine Directive 2006/42/EC.</text>
            </langStringTextType>
          </description>
          <typeValueListElement>SubmodelElementCollection</typeValueListElement>
          <orderRelevant>false</orderRelevant>
          <semanticId>
            <type>ExternalReference</type>
            <keys>
              <key>
                <type>GlobalReference</type>
                <value>0173-1#01-AGZ673#001</value>
              </key>
            </keys>
          </semanticId>
          <semanticIdListElement>
              <type>ExternalReference</type>
              <keys>
                  <key>
                      <type>GlobalReference</type>
                      <value>0173-1#01-AHD206#001</value>
                  </key>
              </keys>
          </semanticIdListElement>
          <qualifiers>
            <qualifier>
              <type>Multiplicity</type>
              <valueType>xs:string</valueType>
              <value>ZeroToOne</value>
            </qualifier>
          </qualifiers>
          <value>
            <submodelElementCollection>
              <idShort>Marking</idShort>
              <description>
                <langStringTextType>
                  <language>en</language>
                  <text>Note: see also [IRDI] 0112/2///61987#ABH515#003 Certificate or approval Note: CE marking is declared as mandatory according to the Blue Guide of the EU-Commission </text>
                </langStringTextType>
              </description>
              <semanticId>
                <type>ExternalReference</type>
                <keys>
                  <key>
                    <type>GlobalReference</type>
                    <value>0173-1#01-AHD206#001</value>
                  </key>
                </keys>
              </semanticId>
              <value>
                <property>
                  <idShort>ExpiryDate</idShort>
                  <description>
                    <langStringTextType>
                      <language>en</language>
                      <text>Note: see also ([IRDI] 0173-1#02-AAO997#001 Validity date Note: format by lexical representation: CCYY-MM-DD Note: to be specified to the day </text>
                    </langStringTextType>
                  </description>
                  <semanticId>
                    <type>ExternalReference</type>
                    <keys>
                      <key>
                        <type>GlobalReference</type>
                        <value>https://admin-shell.io/zvei/nameplate/2/0/Nameplate/Markings/Marking/ExpiryDate</value>
                      </key>
                    </keys>
                  </semanticId>
                  <qualifiers>
                    <qualifier>
                      <type>Multiplicity</type>
                      <valueType>xs:string</valueType>
                      <value>ZeroToOne</value>
                    </qualifier>
                  </qualifiers>
                  <valueType>xs:string</valueType>
                  <value>2022-01-01</value>
                </property>
                <submodelElementList>
                  <idShort>ExplosionSafeties</idShort>
                  <typeValueListElement>SubmodelElementCollection</typeValueListElement>
                  <orderRelevant>false</orderRelevant>
                  <semanticId>
                    <type>ExternalReference</type>
                    <keys>
                      <key>
                        <type>GlobalReference</type>
                        <value>https://admin-shell.io/zvei/nameplate/2/0/Nameplate/Markings/Marking/ExplosionSafeties</value>
                      </key>
                    </keys>
                  </semanticId>
                  <semanticIdListElement>
                      <type>ExternalReference</type>
                      <keys>
                          <key>
                              <type>GlobalReference</type>
                              <value>https://admin-shell.io/zvei/nameplate/2/0/Nameplate/Markings/Marking/ExplosionSafeties/ExplosionSafety</value>
                          </key>
                      </keys>
                  </semanticIdListElement>
                  <qualifiers>
                    <qualifier>
                      <type>Multiplicity</type>
                      <valueType>xs:string</valueType>
                      <value>ZeroToOne</value>
                    </qualifier>
                  </qualifiers>
                  <value>
                    <submodelElementCollection>
                      <idShort>ExplosionSafety</idShort>
                      <semanticId>
                        <type>ExternalReference</type>
                        <keys>
                          <key>
                            <type>GlobalReference</type>
                            <value>https://admin-shell.io/zvei/nameplate/2/0/Nameplate/Markings/Marking/ExplosionSafeties/ExplosionSafety</value>
                          </key>
                        </keys>
                      </semanticId>
                      <qualifiers>
                        <qualifier>
                          <type>Multiplicity</type>
                          <valueType>xs:string</valueType>
                          <value>OneToMany</value>
                        </qualifier>
                      </qualifiers>
                      <value>
                        <property>
                          <idShort>DesignationOfCertificateOrApproval</idShort>
                          <description>
                            <langStringTextType>
                              <language>en</language>
                              <text>Note: Approval identifier, reference to the certificate number, to be entered without spaces </text>
                            </langStringTextType>
                          </description>
                          <semanticId>
                            <type>ExternalReference</type>
                            <keys>
                              <key>
                                <type>GlobalReference</type>
                                <value>0112/2///61987#ABH783#001</value>
                              </key>
                            </keys>
                          </semanticId>
                          <qualifiers>
                            <qualifier>
                              <type>Multiplicity</type>
                              <valueType>xs:string</valueType>
                              <value>ZeroToOne</value>
                            </qualifier>
                          </qualifiers>
                          <valueType>xs:string</valueType>
                          <value>KEMA99IECEX1105/128</value>
                        </property>
                        <multiLanguageProperty>
                          <idShort>TypeOfApproval</idShort>
                          <description>
                            <langStringTextType>
                              <language>en</language>
                              <text>Note: see also [IRDI] 0112/2///61987#ABA231#008 type of hazardous area approval Note: name of the approval system, e.g. ATEX, IECEX, NEC, EAC, CCC, CEC Note: only values from the enumeration should be used as stated. For additional systems further values can be used. Note: Recommendation: property declaration as MLP is required by its semantic definition. As the property value is language independent, users are recommended to provide maximal 1 string in any language of the user’s choice.</text>
                            </langStringTextType>
                          </description>
                          <semanticId>
                            <type>ExternalReference</type>
                            <keys>
                              <key>
                                <type>GlobalReference</type>
                                <value>0173-1#02-AAM812#003</value>
                              </key>
                            </keys>
                          </semanticId>
                          <qualifiers>
                            <qualifier>
                              <type>Multiplicity</type>
                              <valueType>xs:string</valueType>
                              <value>ZeroToOne</value>
                            </qualifier>
                          </qualifiers>
                          <value>
                            <langStringTextType>
                              <language>en</language>
                              <text>ATEX</text>
                            </langStringTextType>
                          </value>
                        </multiLanguageProperty>
                        <property>
                          <idShort>IncompleteDevice</idShort>
                          <semanticId>
                            <type>ExternalReference</type>
                            <keys>
                              <key>
                                <type>GlobalReference</type>
                                <value>https://admin-shell.io/zvei/nameplate/2/0/Nameplate/Markings/Marking/ExplosionSafeties/ExplosionSafety/IncompleteDevice</value>
                              </key>
                            </keys>
                          </semanticId>
                          <qualifiers>
                            <qualifier>
                              <type>Multiplicity</type>
                              <valueType>xs:string</valueType>
                              <value>ZeroToOne</value>
                            </qualifier>
                          </qualifiers>
                          <valueType>xs:string</valueType>
                          <value>U</value>
                        </property>
                        <submodelElementCollection>
                          <idShort>AmbientConditions</idShort>
                          <description>
                            <langStringTextType>
                              <language>en</language>
                              <text>Note: If the device is mounted in the process boundary, ambient and process conditions are provided separately. </text>
                            </langStringTextType>
                          </description>
                          <semanticId>
                            <type>ExternalReference</type>
                            <keys>
                              <key>
                                <type>GlobalReference</type>
                                <value>https://admin-shell.io/zvei/nameplate/2/0/Nameplate/Markings/Marking/ExplosionSafeties/ExplosionSafety/AmbientConditions</value>
                              </key>
                            </keys>
                          </semanticId>
                          <qualifiers>
                            <qualifier>
                              <type>Multiplicity</type>
                              <valueType>xs:string</valueType>
                              <value>ZeroToOne</value>
                            </qualifier>
                          </qualifiers>
                          <value>
                            <property>
                              <idShort>DeviceCategory</idShort>
                              <description>
                                <langStringTextType>
                                  <language>en</language>
                                  <text>Note: see also [IRDI] 0112/2///61987#ABA467#002 equipment/device category Note: editorial definiton: Category of device in accordance with directive 2014/34/EU Note: Equipment category according to the ATEX system. According to the current nameplate, also the combination “GD” is permitted Note: The combination “GD” is no longer accepted and was changed in the standards. Currently the marking for “G” and “D” must be provided in a separate marking string. Older devices may still exist with the marking “GD”. </text>
                                </langStringTextType>
                              </description>
                              <semanticId>
                                <type>ExternalReference</type>
                                <keys>
                                  <key>
                                    <type>GlobalReference</type>
                                    <value>0173-1#02-AAK297#004</value>
                                  </key>
                                </keys>
                              </semanticId>
                              <qualifiers>
                                <qualifier>
                                  <type>Multiplicity</type>
                                  <valueType>xs:string</valueType>
                                  <value>ZeroToOne</value>
                                </qualifier>
                              </qualifiers>
                              <valueType>xs:string</valueType>
                              <value>2G</value>
                            </property>
                            <multiLanguageProperty>
                              <idShort>EquipmentProtectionLevel</idShort>
                              <description>
                                <langStringTextType>
                                  <language>en</language>
                                  <text>Note: see also [IRDI] 0112/2///61987#ABA464#005 equipment protection level Note: editorial definition: Level of protection assigned to equipment based on its likelihood of becoming a source of ignition Note: Equipment protection level according to the IEC standards. According to the current nameplate, also the combination “GD” is permitted Note: The combination “GD” is no longer accepted and was changed in the standards. Currently the marking for “G” and “D” must be provided in a separate marking string. Older devices may still exist with the marking “GD”. Note: Recommendation: property declaration as MLP is required by its semantic definition. As the property value is language independent, users are recommended to provide maximal 1 string in any language of the user’s choice.</text>
                                </langStringTextType>
                              </description>
                              <semanticId>
                                <type>ExternalReference</type>
                                <keys>
                                  <key>
                                    <type>GlobalReference</type>
                                    <value>0173-1#02-AAM668#001</value>
                                  </key>
                                </keys>
                              </semanticId>
                              <qualifiers>
                                <qualifier>
                                  <type>Multiplicity</type>
                                  <valueType>xs:string</valueType>
                                  <value>ZeroToOne</value>
                                </qualifier>
                              </qualifiers>
                              <value>
                                <langStringTextType>
                                  <language>en</language>
                                  <text>Gb</text>
                                </langStringTextType>
                              </value>
                            </multiLanguageProperty>
                            <property>
                              <idShort>RegionalSpecificMarking</idShort>
                              <semanticId>
                                <type>ExternalReference</type>
                                <keys>
                                  <key>
                                    <type>GlobalReference</type>
                                    <value>https://admin-shell.io/zvei/nameplate/2/0/Nameplate/Markings/Marking/ExplosionSafeties/ExplosionSafety/RegionalSpecificMarking</value>
                                  </key>
                                </keys>
                              </semanticId>
                              <qualifiers>
                                <qualifier>
                                  <type>Multiplicity</type>
                                  <valueType>xs:string</valueType>
                                  <value>ZeroToOne</value>
                                </qualifier>
                              </qualifiers>
                              <valueType>xs:string</valueType>
                              <value>Class I, Division 2</value>
                            </property>
                            <property>
                              <idShort>TypeOfProtection</idShort>
                              <description>
                                <langStringTextType>
                                  <language>en</language>
                                  <text>Note: see also [IRDI] 0112/2///61987#ABA589#002 type of protection (Ex) Note: Symbol(s) for the Type of protection. Several types of protection are separated by a semicolon “;” </text>
                                </langStringTextType>
                              </description>
                              <semanticId>
                                <type>ExternalReference</type>
                                <keys>
                                  <key>
                                    <type>GlobalReference</type>
                                    <value>0173-1#02-AAQ325#003</value>
                                  </key>
                                </keys>
                              </semanticId>
                              <qualifiers>
                                <qualifier>
                                  <type>Multiplicity</type>
                                  <valueType>xs:string</valueType>
                                  <value>ZeroToOne</value>
                                </qualifier>
                              </qualifiers>
                              <valueType>xs:string</valueType>
                              <value>db</value>
                            </property>
                            <property>
                              <idShort>ExplosionGroup</idShort>
                              <description>
                                <langStringTextType>
                                  <language>en</language>
                                  <text>Note: see also [IRDI] 0112/2///61987#ABA961#007 permitted gas group/explosion group Note: Equipment grouping according to IEC 60079-0 is meant by this property Note: Symbol(s) for the gas group (IIA…IIC) or dust group (IIIA…IIIC) </text>
                                </langStringTextType>
                              </description>
                              <semanticId>
                                <type>ExternalReference</type>
                                <keys>
                                  <key>
                                    <type>GlobalReference</type>
                                    <value>0173-1#02-AAT372#001</value>
                                  </key>
                                </keys>
                              </semanticId>
                              <qualifiers>
                                <qualifier>
                                  <type>Multiplicity</type>
                                  <valueType>xs:string</valueType>
                                  <value>ZeroToOne</value>
                                </qualifier>
                              </qualifiers>
                              <valueType>xs:string</valueType>
                              <value>IIC</value>
                            </property>
                            <property>
                              <idShort>MinimumAmbientTemperature</idShort>
                              <description>
                                <langStringTextType>
                                  <language>en</language>
                                  <text>Note: see also [IRDI] 0112/2///61987#ABA621#007 minimum ambient temperature Note: editorial defnition: lower limit of the temperature range of the environment in which the component, the pipework or the system can be operated Note: Rated minimum ambient temperature Note: Positive temperatures are listed without “+” sign. If several temperatures ranges are marked, only the most general range shall be indicated in the template, which is consistent with the specified temperature class or maximum surface temperature. Other temperature ranges and temperature classes/maximum surface temperatures may be listed in the instructions.</text>
                                </langStringTextType>
                              </description>
                              <semanticId>
                                <type>ExternalReference</type>
                                <keys>
                                  <key>
                                    <type>GlobalReference</type>
                                    <value>0173-1#02-AAZ952#001</value>
                                  </key>
                                </keys>
                              </semanticId>
                              <qualifiers>
                                <qualifier>
                                  <type>Multiplicity</type>
                                  <valueType>xs:string</valueType>
                                  <value>ZeroToOne</value>
                                </qualifier>
                              </qualifiers>
                              <valueType>xs:string</valueType>
                              <value>-40</value>
                            </property>
                            <property>
                              <idShort>MaxAmbientTemperature</idShort>
                              <description>
                                <langStringTextType>
                                  <language>en</language>
                                  <text>Note: see also [IRDI] 0112/2///61987#ABA623#007 maximum ambient temperature Note: editorial definition: upper limit of the temperature range of the environment in which the component, the pipework or the system can be operated Note: Rated maximum ambient temperature Note: Positive temperatures are listed without “+” sign. If several temperatures ranges are marked, only the most general range shall be indicated in the template, which is consistent with the specified temperature class or maximum surface temperature. Other temperature ranges and temperature classes/maximum surface temperatures may be listed in the instructions.</text>
                                </langStringTextType>
                              </description>
                              <semanticId>
                                <type>ExternalReference</type>
                                <keys>
                                  <key>
                                    <type>GlobalReference</type>
                                    <value>0173-1#02-BAA039#010</value>
                                  </key>
                                </keys>
                              </semanticId>
                              <qualifiers>
                                <qualifier>
                                  <type>Multiplicity</type>
                                  <valueType>xs:string</valueType>
                                  <value>ZeroToOne</value>
                                </qualifier>
                              </qualifiers>
                              <valueType>xs:string</valueType>
                              <value>120</value>
                            </property>
                            <property>
                              <idShort>MaxSurfaceTemperatureForDustProof</idShort>
                              <description>
                                <langStringTextType>
                                  <language>en</language>
                                  <text>Note: see also [IRDI] 0112/2///61987#ABB159#004 maximum surface temperature for dust-proof Note: Maximum surface temperature of the device (dust layer ≤ 5 mm) for specified maximum ambient and maximum process temperature, relevant for Group III only Note: Positive temperatures are listed without “+” sign. If several temperatures ranges are marked, only the most general range shall be indicated in the template, which is consistent with the specified temperature class or maximum surface temperature. Other temperature ranges and temperature classes/maximum surface temperatures may be listed in the instructions.</text>
                                </langStringTextType>
                              </description>
                              <semanticId>
                                <type>ExternalReference</type>
                                <keys>
                                  <key>
                                    <type>GlobalReference</type>
                                    <value>0173-1#02-AAM666#005</value>
                                  </key>
                                </keys>
                              </semanticId>
                              <qualifiers>
                                <qualifier>
                                  <type>Multiplicity</type>
                                  <valueType>xs:string</valueType>
                                  <value>ZeroToOne</value>
                                </qualifier>
                              </qualifiers>
                              <valueType>xs:string</valueType>
                              <value>100</value>
                            </property>
                            <property>
                              <idShort>TemperatureClass</idShort>
                              <description>
                                <langStringTextType>
                                  <language>en</language>
                                  <text>Note: see also [IRDI] 0112/2///61987#ABA593#002 temperature class Note: editorial definition: classification system of electrical apparatus, based on its maximum surface temperature, intended for use in an explosive atmospheres with flammable gas, vapour or mist. Note: Temperature class for specified maximum ambient and maximum process temperature, relevant for Group II only (Further combinations may be provided in the instruction manual). </text>
                                </langStringTextType>
                              </description>
                              <semanticId>
                                <type>ExternalReference</type>
                                <keys>
                                  <key>
                                    <type>GlobalReference</type>
                                    <value>0173-1#02-AAO371#004</value>
                                  </key>
                                </keys>
                              </semanticId>
                              <qualifiers>
                                <qualifier>
                                  <type>Multiplicity</type>
                                  <valueType>xs:string</valueType>
                                  <value>ZeroToOne</value>
                                </qualifier>
                              </qualifiers>
                              <valueType>xs:string</valueType>
                              <value>T4</value>
                            </property>
                          </value>
                        </submodelElementCollection>
                        <submodelElementCollection>
                          <idShort>ProcessConditions</idShort>
                          <description>
                            <langStringTextType>
                              <language>en</language>
                              <text>Note: If the device is mounted in the process boundary, ambient and process conditions are provided separately. </text>
                            </langStringTextType>
                          </description>
                          <semanticId>
                            <type>ExternalReference</type>
                            <keys>
                              <key>
                                <type>GlobalReference</type>
                                <value>https://admin-shell.io/zvei/nameplate/2/0/Nameplate/Markings/Marking/ExplosionSafeties/ExplosionSafety/ProcessConditions</value>
                              </key>
                            </keys>
                          </semanticId>
                          <qualifiers>
                            <qualifier>
                              <type>Multiplicity</type>
                              <valueType>xs:string</valueType>
                              <value>ZeroToOne</value>
                            </qualifier>
                          </qualifiers>
                          <value>
                            <property>
                              <idShort>DeviceCategory</idShort>
                              <description>
                                <langStringTextType>
                                  <language>en</language>
                                  <text>Note: see also [IRDI] 0112/2///61987#ABA467#002 equipment/device category Note: editorial defnition: Category of device in accordance with directive 2014/34/EU Note: Equipment category according to the ATEX system. </text>
                                </langStringTextType>
                              </description>
                              <semanticId>
                                <type>ExternalReference</type>
                                <keys>
                                  <key>
                                    <type>GlobalReference</type>
                                    <value>0173-1#02-AAK297#004</value>
                                  </key>
                                </keys>
                              </semanticId>
                              <qualifiers>
                                <qualifier>
                                  <type>Multiplicity</type>
                                  <valueType>xs:string</valueType>
                                  <value>ZeroToOne</value>
                                </qualifier>
                              </qualifiers>
                              <valueType>xs:string</valueType>
                              <value>1G</value>
                            </property>
                          </value>
                        </submodelElementCollection>
                      </value>
                    </submodelElementCollection>
                  </value>
                </submodelElementList>
              </value>
            </submodelElementCollection>
          </value>
        </submodelElementList>
      </submodelElements>
    </submodel>
  </submodels>
  <conceptDescriptions>
  </conceptDescriptions>
</environment>
"""

        # NOTE (mristin, 2024-02-14):
        # This statement raised the exception before the fix. Strangely enough,
        # when the indention of the XML text changed, there was no error. This might
        # have something to do with the buffer size, but we are not sure.
        #
        # For example, if you change the indention of the XML, there would be no error.
        _ = aas_xmlization.environment_from_str(text)


class TestOnXSIAttributes(unittest.TestCase):
    """
    Test how we can deal gracefully with common ``xsi:`` attributes.

    The specification does not allow any XML attributes, but many applications simply
    add ``xsi`` attributes by default.

    See:
    https://github.com/aas-core-works/aas-core3.0-python/issues/44
    """

    def test_pipeline_approach(self) -> None:
        text = """\
<?xml version="1.0" encoding="UTF-8"?>
<environment
    xmlns="https://admin-shell.io/aas/3/0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="https://admin-shell.io/aas/3/0/AAS.xsd">
</environment>
"""

        iterator = xml.etree.ElementTree.iterparse(
            io.StringIO(text), events=("start", "end")
        )

        def with_attributes_removed(
            an_iterator: Iterator[Tuple[str, xml.etree.ElementTree.Element]]
        ) -> Iterator[Tuple[str, xml.etree.ElementTree.Element]]:
            """
            Map the :paramref:`iterator` such that all attributes are removed.

            :param an_iterator: to be mapped
            :yield: event and element without attributes from :paramref:`iterator`
            """
            for event, element in an_iterator:
                element.attrib.clear()

                yield event, element

        environment = aas_xmlization.environment_from_iterparse(
            iterator=with_attributes_removed(iterator)
        )

        # NOTE (mristin):
        # The attributes are lost in the subsequent serialization.
        serialization = aas_xmlization.to_str(environment)

        self.assertEqual(
            '<environment xmlns="https://admin-shell.io/aas/3/0"/>',
            serialization,
        )


if __name__ == "__main__":
    unittest.main()
