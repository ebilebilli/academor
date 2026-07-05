"""IELTS Academic Reading topic bank: practice tests 2–26."""

TOPICS = [{'quiz_number': 2,
  'title': 'Quantum Computing and Cryptography',
  'topic_category': 'Science',
  'paragraphs': {'A': 'Quantum computers exploit superposition and entanglement to perform '
                      'selected calculations far faster than classical machines. Researchers have '
                      'warned that this capability could undermine widely deployed encryption, '
                      'because many security protocols depend on mathematical problems that remain '
                      'intractable for conventional hardware. Although useful quantum devices are '
                      'still limited in scale, steady improvements in qubit count and error '
                      'correction have renewed debate among policymakers and industry leaders '
                      'about how urgently communication networks must be upgraded before '
                      'confidential data becomes vulnerable to retrospective decryption by '
                      'well-resourced adversaries operating across borders and jurisdictions with '
                      'uneven regulatory maturity in practice.',
                 'B': 'Public-key cryptography, including RSA, relies on the difficulty of '
                      'factoring very large integers into prime components. Classical algorithms '
                      'require exponential time for this task, which is why banks, governments, '
                      'and e-commerce platforms have trusted these schemes for decades without '
                      "routine breach. Shor's algorithm, however, could factor large numbers in "
                      'polynomial time on a sufficiently powerful quantum computer. Experts '
                      'estimate that thousands of stable logical qubits might be needed before '
                      'such an attack becomes practical, yet the threshold is no longer considered '
                      'purely theoretical by national security agencies monitoring hardware '
                      'progress in competing research laboratories worldwide.',
                 'C': 'In response, cryptographers are designing post-quantum algorithms believed '
                      'to resist both classical and quantum adversaries. Lattice-based and '
                      'hash-based schemes are leading candidates in international standardisation '
                      'efforts coordinated through public competitions and peer review. Transition '
                      'planning is complicated because legacy systems cannot always be patched '
                      'quickly, and organisations must inventory where vulnerable algorithms '
                      'appear in software libraries, hardware security modules, and archived '
                      'records that could be decrypted later if ciphertext is harvested and stored '
                      'today by patient adversaries awaiting future breakthroughs in scalable '
                      'hardware deployed outside laboratory conditions by state-sponsored '
                      'programmes worldwide today already in practice.',
                 'D': 'Quantum key distribution offers a complementary approach by using quantum '
                      'states to detect eavesdropping on fibre links. If an intruder measures '
                      'photons en route, the disturbance reveals the breach and the keys are '
                      'discarded before secure communication proceeds. Proponents argue that this '
                      'method provides information-theoretic security for key exchange, though '
                      'critics note that practical deployments face distance limits, high costs, '
                      'and the need for trusted classical authentication layers that themselves '
                      'may require post-quantum protection before end-to-end systems are genuinely '
                      'future-proof in heterogeneous networks spanning campuses, metropolitan '
                      'areas, and submarine cables owned by competing carriers and consortium '
                      'partners.',
                 'E': 'National agencies have begun publishing migration timelines urging '
                      'operators to adopt hybrid classical and post-quantum protocols during a '
                      'lengthy overlap period. The author contends that panic is unwarranted '
                      'because cryptanalytically relevant machines are unlikely to appear without '
                      'prior warning, yet delaying inventory work is equally unwise. '
                      'Harvest-now-decrypt-later strategies, in which adversaries store encrypted '
                      'traffic today for future decoding, mean that sensitive long-lived data such '
                      'as diplomatic cables, medical records, and trade secrets may already be at '
                      'risk even before quantum hardware matures commercially in any single '
                      'jurisdiction or export-controlled facility subject to trade sanctions and '
                      'monitoring.',
                 'F': 'Corporate security teams report uneven readiness across sectors. Financial '
                      'institutions have funded pilot projects and vendor evaluations, whereas '
                      'smaller software vendors lack expertise to assess marketing claims about '
                      'quantum safety. Certification frameworks are emerging, but buyers struggle '
                      'to distinguish promotional language from peer-reviewed cryptographic '
                      'designs. Training programmes for developers remain scarce, which slows '
                      'replacement of hard-coded algorithms embedded deep inside enterprise '
                      'resource planning systems, industrial control software, and firmware that '
                      'cannot be updated remotely without costly downtime and contractual '
                      'renegotiation with integrators and maintenance contractors serving critical '
                      'infrastructure operators nationwide today already in practice now.',
                 'G': 'Looking ahead, the author believes cryptography will remain viable if '
                      'societies treat the transition as a managed engineering programme rather '
                      'than a sudden crisis. Standards bodies, universities, and cloud providers '
                      'must coordinate interoperability testing so that performance penalties on '
                      'mobile devices, smart cards, and embedded sensors are understood before '
                      'mandatory deadlines arrive. Ultimately, quantum technology threatens '
                      'specific mathematical assumptions, not the broader goal of confidential '
                      'communication, provided institutions begin systematic upgrades soon rather '
                      'than postponing decisions until migration becomes chaotic and disruptive '
                      'for citizens and small enterprises alike that depend on digital services '
                      'daily worldwide.'},
  'tfng': [{'question': 'Quantum computers can already break all forms of encryption in current '
                        'use.',
            'answer': 'False'},
           {'question': "Shor's algorithm relates to factoring large numbers.", 'answer': 'True'},
           {'question': 'Every organisation has completed an inventory of vulnerable algorithms.',
            'answer': 'Not Given'},
           {'question': 'Quantum key distribution can reveal when a communication line has been '
                        'interfered with.',
            'answer': 'True'},
           {'question': 'The author states that useful quantum code-breaking machines will '
                        'certainly appear without warning.',
            'answer': 'False'}],
  'ynng': [{'question': 'The author believes immediate panic over quantum threats is justified.',
            'answer': 'No'},
           {'question': 'The writer agrees that storing encrypted data now creates future risk '
                        'under harvest-now-decrypt-later attacks.',
            'answer': 'Yes'},
           {'question': 'The author thinks quantum key distribution alone removes the need for '
                        'classical authentication.',
            'answer': 'No'},
           {'question': 'The writer claims smaller vendors are generally well prepared for '
                        'post-quantum migration.',
            'answer': 'No'},
           {'question': 'The author is confident that confidentiality can be preserved through '
                        'careful upgrading.',
            'answer': 'Yes'}],
  'matching_headings': [{'paragraph': 'B',
                         'correct': 'ii. A classical security assumption under threat'},
                        {'paragraph': 'C',
                         'correct': 'iv. Designing replacements and managing legacy systems'},
                        {'paragraph': 'D',
                         'correct': 'iii. Photonic methods for detecting interception'},
                        {'paragraph': 'E',
                         'correct': "v. Timelines, stored traffic, and the author's caution"},
                        {'paragraph': 'F',
                         'correct': 'vi. Unequal corporate preparedness and certification gaps'}],
  'headings_pool': ['i. University courses on quantum physics fundamentals',
                    'ii. A classical security assumption under threat',
                    'iii. Photonic methods for detecting interception',
                    'iv. Designing replacements and managing legacy systems',
                    "v. Timelines, stored traffic, and the author's caution",
                    'vi. Unequal corporate preparedness and certification gaps',
                    'vii. Consumer demand for faster mobile applications'],
  'matching_info': [{'question': 'a mention of algorithms that may resist quantum attacks',
                     'paragraph': 'C'},
                    {'question': 'reference to photons being measured by an intruder',
                     'paragraph': 'D'},
                    {'question': 'examples of sectors with different levels of preparation',
                     'paragraph': 'F'},
                    {'question': 'discussion of superposition and entanglement', 'paragraph': 'A'},
                    {'question': 'a positive outlook on maintaining confidential communication',
                     'paragraph': 'G'}],
  'sentence_completion': [{'question': 'Many security protocols depend on mathematical problems '
                                       'that are difficult for ____ hardware.',
                           'answer': 'conventional'},
                          {'question': "Shor's algorithm could factor large numbers in ____ time "
                                       'on a powerful quantum computer.',
                           'answer': 'polynomial'},
                          {'question': 'Quantum key distribution can detect eavesdropping by '
                                       'observing disturbance to ____ states.',
                           'answer': 'quantum'},
                          {'question': 'The author recommends treating the transition as a managed '
                                       '____ programme.',
                           'answer': 'engineering'}],
  'summary_completion': [{'question': 'Public-key schemes such as RSA rely on the hardness of '
                                      'factoring large ____. Post-quantum research includes '
                                      'lattice-based designs.',
                          'answer': 'integers'},
                         {'question': 'Adversaries may use harvest-now-decrypt-later tactics by '
                                      'storing ____ today.',
                          'answer': 'ciphertext'},
                         {'question': 'Buyers find it hard to separate marketing claims from ____ '
                                      'designs.',
                          'answer': 'peer-reviewed'},
                         {'question': 'Cloud providers should coordinate testing before mandatory '
                                      '____ arrive.',
                          'answer': 'deadlines'}],
  'table_completion': [{'question': "Threat mechanism | Shor's algorithm targets integer ____",
                        'answer': 'factoring'},
                       {'question': 'QKD limitation | Practical links face distance ____',
                        'answer': 'limits'},
                       {'question': 'Migration approach | Agencies urge ____ classical and '
                                    'post-quantum protocols',
                        'answer': 'hybrid'}],
  'mcq': [{'question': 'What is the main concern about quantum computers in paragraph A?',
           'options': ['They consume too much electricity for data centres.',
                       'They could defeat encryption based on hard mathematical problems.',
                       'They have replaced classical machines in banking networks.',
                       'They make training programmers unnecessary.'],
           'answer': 'They could defeat encryption based on hard mathematical problems.'},
          {'question': "According to paragraph B, when might Shor's algorithm become a practical "
                       'threat?',
           'options': ['Immediately, with current laboratory devices',
                       'Only if thousands of stable logical qubits exist',
                       'After all smartphones are upgraded',
                       'When RSA keys are shortened deliberately'],
           'answer': 'Only if thousands of stable logical qubits exist'},
          {'question': 'Paragraph D suggests a limitation of quantum key distribution is that',
           'options': ['it cannot operate over any distance',
                       'it eliminates the need for keys entirely',
                       'deployments still depend on classical authentication layers',
                       'it is illegal in most countries'],
           'answer': 'deployments still depend on classical authentication layers'},
          {'question': 'The author uses the term harvest-now-decrypt-later to describe',
           'options': ['farmers selling encrypted produce online',
                       'storing ciphertext now for decoding when quantum tools mature',
                       'deleting old archives before migration',
                       'harvesting qubits from defective chips'],
           'answer': 'storing ciphertext now for decoding when quantum tools mature'},
          {'question': 'The concluding paragraph argues that',
           'options': ['confidential communication is impossible after quantum advances',
                       'only universities should manage cryptographic standards',
                       'systematic upgrades can preserve confidentiality',
                       'mobile performance penalties should block all change'],
           'answer': 'systematic upgrades can preserve confidentiality'}],
  'short_answer': [{'question': 'Which algorithm is named as a threat to factoring-based '
                                'cryptography?',
                    'answer': "Shor's",
                    'word_limit': 1},
                   {'question': 'What mineral-like term describes one family of post-quantum '
                                'candidate schemes?',
                    'answer': 'lattice-based',
                    'word_limit': 2},
                   {'question': 'What type of institutions are urged to coordinate testing with '
                                'cloud providers?',
                    'answer': 'standards bodies',
                    'word_limit': 2},
                   {'question': 'What kind of penalties on mobile devices must be understood '
                                'before deadlines?',
                    'answer': 'performance',
                    'word_limit': 1}]},
 {'quiz_number': 3,
  'title': 'CRISPR Gene Editing',
  'topic_category': 'Science',
  'paragraphs': {'A': 'Clustered regularly interspaced short palindromic repeats, known as CRISPR, '
                      'have transformed molecular biology by enabling precise edits to DNA '
                      'sequences in living cells. Originally discovered as an adaptive immune '
                      'system in bacteria, the toolkit now allows researchers to target specific '
                      'genes with remarkable accuracy compared with earlier nuclease technologies '
                      'such as zinc-finger proteins. Laboratories worldwide have adopted the '
                      'method for basic research, drug discovery, and agricultural breeding, '
                      'although practical outcomes still depend on delivery efficiency, off-target '
                      'effects, and the complexity of the trait being modified in each organism '
                      'and environmental context under field conditions monitored across seasons.',
                 'B': 'The most widely used variant pairs the Cas9 enzyme with a synthetic guide '
                      'RNA that directs cutting to a complementary genomic site. Once '
                      'double-strand breaks occur, cellular repair pathways introduce insertions '
                      'or deletions, or researchers supply a donor template to rewrite the '
                      'sequence with intended changes. Base editors and prime editors refine this '
                      'approach by changing individual letters without fully severing the DNA '
                      'backbone, potentially reducing unwanted rearrangements. These refinements '
                      'illustrate how quickly the field has moved from proof-of-concept papers to '
                      'diversified editing platforms suitable for distinct therapeutic and '
                      'agricultural goals across public and private laboratories.',
                 'C': 'Clinical trials are exploring CRISPR-based therapies for blood disorders, '
                      'certain cancers, and inherited metabolic conditions. Ex vivo approaches '
                      'modify patient cells outside the body before reinfusion, which simplifies '
                      'quality control and dosing review by regulators. In vivo delivery remains '
                      'more challenging because viral vectors and lipid nanoparticles must reach '
                      'the correct tissue while limiting immune reactions that could destroy '
                      'edited cells prematurely. Early results have encouraged investment, yet '
                      'long-term monitoring is essential to detect delayed adverse events that '
                      'might not appear in short follow-up windows reported in initial trial '
                      'publications and conference abstracts reviewed by independent safety '
                      'boards.',
                 'D': 'Germline editing, which would alter eggs, sperm, or embryos, raises '
                      'profound ethical questions because changes could pass to future generations '
                      'without their consent. International commissions have called for cautious '
                      'moratoria except in narrow research settings, while the author argues that '
                      'transparent governance is preferable to unregulated experimentation '
                      'conducted beyond public scrutiny. Public consultation reveals uneven '
                      'understanding of risks, suggesting that science communication must improve '
                      'before societies can make informed policy choices about reproductive '
                      'applications that could reshape human genetic diversity in unpredictable '
                      'ways across communities with differing cultural values and religious '
                      'traditions worldwide today already.',
                 'E': 'Agricultural scientists employ CRISPR to enhance drought tolerance, reduce '
                      'allergenic proteins, and accelerate conventional breeding timelines without '
                      'introducing foreign transgenes in some jurisdictions. Regulators in several '
                      'countries distinguish such edits from transgenic crops that incorporate '
                      'foreign DNA, though labeling debates continue among consumer groups and '
                      'exporters. Critics worry that commercial pressure could narrow crop '
                      'diversity, whereas proponents maintain that precise edits may reduce '
                      'reliance on broad-spectrum chemical sprays if resistance traits are '
                      'deployed responsibly within integrated pest management programmes on mixed '
                      'farms and cooperatives worldwide subject to seasonal monitoring and '
                      'independent audits by regulators annually.',
                 'F': 'Intellectual property disputes and licensing fees influence who benefits '
                      'from the technology. Universities and biotechnology firms hold overlapping '
                      'patents on core components, which can hinder researchers in low-income '
                      'settings seeking affordable diagnostics and therapies. Open-science '
                      'advocates promote shared repositories of guide RNA designs, yet quality '
                      'assurance remains uneven when sequences are contributed without independent '
                      'validation. The author contends that equitable access requires both legal '
                      'clarity and funding mechanisms that support non-profit applications '
                      'addressing neglected tropical diseases overlooked by commercial investors '
                      'focused on affluent markets and blockbuster indications with predictable '
                      'reimbursement pathways in public health systems.',
                 'G': 'Looking forward, CRISPR is unlikely to replace every older genetic tool, '
                      'but it has become a standard instrument in the life sciences curriculum and '
                      'industrial pipelines. Continued advances in delivery, specificity, and '
                      'computational off-target prediction will determine whether therapeutic '
                      'promises scale beyond boutique interventions for rare conditions. If '
                      'oversight keeps pace with capability, the author believes society can '
                      'harness precise genome editing while limiting reckless uses that could '
                      'erode public trust in biomedical research and trigger restrictive bans on '
                      'valuable somatic therapies with broad clinical benefit for common disorders '
                      'affecting ageing populations globally today already.'},
  'tfng': [{'question': 'CRISPR was first identified as part of a bacterial immune mechanism.',
            'answer': 'True'},
           {'question': 'All CRISPR therapies currently approved use in vivo delivery only.',
            'answer': 'False'},
           {'question': 'Prime editors always create large deletions across entire chromosomes.',
            'answer': 'False'},
           {'question': 'International bodies have encouraged completely unrestricted germline '
                        'editing.',
            'answer': 'False'},
           {'question': 'The passage states that every country labels CRISPR crops identically.',
            'answer': 'Not Given'}],
  'ynng': [{'question': 'The author prefers transparent governance over unregulated germline '
                        'experimentation.',
            'answer': 'Yes'},
           {'question': 'The writer believes public understanding of editing risks is uniformly '
                        'high.',
            'answer': 'No'},
           {'question': 'The author thinks equitable access depends partly on funding for '
                        'non-profit uses.',
            'answer': 'Yes'},
           {'question': 'The writer claims CRISPR will entirely replace older genetic tools soon.',
            'answer': 'No'},
           {'question': 'The author is optimistic that oversight can keep pace with technical '
                        'capability.',
            'answer': 'Yes'}],
  'matching_headings': [{'paragraph': 'B',
                         'correct': 'ii. Guide molecules and refined cutting tools'},
                        {'paragraph': 'C', 'correct': 'iii. Medical trials and delivery hurdles'},
                        {'paragraph': 'D', 'correct': 'iv. Heritable changes and public policy'},
                        {'paragraph': 'E', 'correct': 'v. Crop traits and regulatory distinctions'},
                        {'paragraph': 'F', 'correct': 'vi. Patents, access, and shared resources'}],
  'headings_pool': ['i. Deep-sea mining permits and seabed law',
                    'ii. Guide molecules and refined cutting tools',
                    'iii. Medical trials and delivery hurdles',
                    'iv. Heritable changes and public policy',
                    'v. Crop traits and regulatory distinctions',
                    'vi. Patents, access, and shared resources',
                    'vii. Quantum tunnelling in enzyme catalysis'],
  'matching_info': [{'question': 'a description of Cas9 paired with synthetic guide RNA',
                     'paragraph': 'B'},
                    {'question': 'mention of ex vivo modification before reinfusion',
                     'paragraph': 'C'},
                    {'question': 'discussion of changes that could affect descendants',
                     'paragraph': 'D'},
                    {'question': 'reference to drought tolerance in plants', 'paragraph': 'E'},
                    {'question': 'a balanced conclusion about public trust', 'paragraph': 'G'}],
  'sentence_completion': [{'question': 'Cas9 creates double-strand breaks that cells repair '
                                       'through natural ____.',
                           'answer': 'pathways'},
                          {'question': 'Base editors can change individual letters without fully '
                                       'severing the DNA ____.',
                           'answer': 'backbone'},
                          {'question': 'In vivo delivery must limit immune ____ while reaching '
                                       'target tissue.',
                           'answer': 'reactions'},
                          {'question': 'Open-science advocates promote shared repositories of '
                                       'guide RNA ____.',
                           'answer': 'designs'}],
  'summary_completion': [{'question': 'CRISPR originated as an adaptive immune system in ____. '
                                      'Early tools included zinc-finger nucleases.',
                          'answer': 'bacteria'},
                         {'question': 'Germline editing could alter eggs, sperm, or ____. '
                                      'Commissions have urged caution.',
                          'answer': 'embryos'},
                         {'question': 'Some regulators distinguish CRISPR crops from transgenic '
                                      'plants carrying foreign ____. ',
                          'answer': 'DNA'},
                         {'question': 'Long-term monitoring is needed to detect delayed adverse '
                                      '____. ',
                          'answer': 'events'}],
  'table_completion': [{'question': 'Editing platform | Prime editors aim to reduce unwanted ____',
                        'answer': 'rearrangements'},
                       {'question': 'Agriculture concern | Critics fear commercial pressure could '
                                    'narrow crop ____',
                        'answer': 'diversity'},
                       {'question': 'Access barrier | Overlapping ____ can hinder low-income '
                                    'researchers',
                        'answer': 'patents'}],
  'mcq': [{'question': 'What advantage of CRISPR is emphasised in paragraph A?',
           'options': ['It requires no laboratory training.',
                       'It enables precise DNA edits compared with earlier tools.',
                       'It eliminates all off-target effects automatically.',
                       'It works only in plants.'],
           'answer': 'It enables precise DNA edits compared with earlier tools.'},
          {'question': 'Paragraph C indicates that in vivo delivery is difficult because',
           'options': ['cells cannot be cultured outside the body',
                       'vectors must reach tissue while controlling immune reactions',
                       'blood disorders cannot be treated genetically',
                       'trials are illegal in every country'],
           'answer': 'vectors must reach tissue while controlling immune reactions'},
          {'question': 'According to paragraph E, some regulators treat certain CRISPR crops '
                       'differently because',
           'options': ['they contain no foreign DNA',
                       'they are always allergenic',
                       'they cannot grow outdoors',
                       'they use larger seeds'],
           'answer': 'they contain no foreign DNA'},
          {'question': 'Paragraph F suggests a barrier for researchers in low-income settings is',
           'options': ['lack of sunlight in laboratories',
                       'overlapping patents and licensing fees',
                       'absence of any guide RNA databases',
                       'ban on university collaboration'],
           'answer': 'overlapping patents and licensing fees'},
          {'question': 'The final paragraph argues that scaling therapies depends on',
           'options': ['replacing all computational tools',
                       'advances in delivery, specificity, and off-target prediction',
                       'ending every clinical trial',
                       'removing moratoria on germline work'],
           'answer': 'advances in delivery, specificity, and off-target prediction'}],
  'short_answer': [{'question': 'Which enzyme is most commonly paired with guide RNA?',
                    'answer': 'Cas9',
                    'word_limit': 1},
                   {'question': 'What editing approach modifies patient cells outside the body?',
                    'answer': 'ex vivo',
                    'word_limit': 2},
                   {'question': 'What type of commissions have called for cautious moratoria on '
                                'germline work?',
                    'answer': 'international',
                    'word_limit': 1},
                   {'question': 'What must science communication improve before informed policy '
                                'choices?',
                    'answer': 'public understanding',
                    'word_limit': 2}]},
 {'quiz_number': 4,
  'title': 'Plate tectonics and seismic risk',
  'topic_category': 'Science',
  'paragraphs': {'A': 'Plate tectonics describes how rigid lithospheric plates glide over the '
                      'ductile asthenosphere, driven by mantle convection, slab pull, and ridge '
                      'push. Earthquake belts and volcanic arcs trace boundaries where stress '
                      'accumulates before sudden rupture releases stored elastic energy across '
                      'vast fault segments. Modern geodetic networks measure millimetre-scale '
                      'crustal strain, helping scientists refine forecasts for megathrust zones '
                      'beside densely populated coastlines and ports. Nevertheless, hazard maps '
                      'stay uncertain where historical catalogues are brief or incomplete, '
                      'limiting confidence in recurrence estimates used for urban planning. Linked '
                      'offshore faults with submarine landslides can amplify tsunami risk beyond '
                      'simple magnitude estimates published in brochures aimed at the general '
                      'public.',
                 'B': 'At convergent margins, oceanic lithosphere subducts beneath continental '
                      'crust, generating deep seismicity and magmatic arcs that shape long-term '
                      'landscape evolution. Friction along locked plate interfaces stores elastic '
                      'energy that may be released during large ruptures spanning hundreds of '
                      'kilometres within minutes. Paleoseismology excavates coastal sediments to '
                      'extend rupture histories beyond instrumental records, revealing recurrence '
                      'intervals that sometimes exceed several centuries. Geophysicists combine '
                      'these timelines with Global Navigation Satellite System measurements to '
                      'estimate remaining slip budgets along heterogeneous fault segments. Such '
                      'integrative work improves awareness yet cannot guarantee precise prediction '
                      'of the day or hour when the next major earthquake will occur.',
                 'C': 'Probabilistic seismic hazard analysis translates geological knowledge into '
                      'ground-motion maps used by structural engineers when designing hospitals, '
                      'bridges, and schools. Attenuation relationships describe how shaking '
                      'weakens with distance, while site effects amplify waves in soft sedimentary '
                      'basins beneath densely built urban districts. Building codes increasingly '
                      'demand performance-based design that limits collapse probability rather '
                      'than prescribing uniform strength factors for every building category. '
                      'Retrofitting older masonry structures remains expensive, and the author '
                      'argues that transparent communication of uncertainty is preferable to '
                      'implying precise forecasts. Communities make better land-use choices when '
                      'scientists explain confidence intervals instead of presenting hazard '
                      'contours as deterministic boundaries on planning maps.',
                 'D': 'Early warning systems exploit the lag between fast but weak primary waves '
                      'and slower, destructive secondary waves travelling through the crust toward '
                      'cities. Dense sensor networks can issue alerts seconds before strong '
                      'shaking reaches urban cores, allowing trains to brake and surgeons to pause '
                      'delicate procedures. False alarms and missed events undermine public trust, '
                      'so operators tune detection thresholds carefully using years of regional '
                      'calibration data. The writer maintains that such systems complement, rather '
                      'than replace, long-term preparedness investments in resilient '
                      'infrastructure and rehearsed evacuation routes. Seconds of warning can '
                      'reduce injuries, yet they cannot eliminate the need for robust buildings '
                      'designed according to updated seismic hazard models.',
                 'E': 'Tsunami modelling couples seafloor deformation with hydrodynamic '
                      'simulations to estimate inundation heights along vulnerable shorelines and '
                      'estuarine channels. Bathymetry errors and uncertain slip distributions '
                      'propagate into wide confidence bands on evacuation maps distributed to '
                      'households and schools. Community drills improve response times, yet '
                      'seasonal tourism and language barriers complicate messaging in '
                      'multicultural ports receiving cruise ships daily. Critics note that '
                      'economic pressure to rebuild quickly after disasters can repeat unsafe '
                      'coastal development unless zoning laws incorporate updated scientific '
                      'assessments. Enforcing setbacks from newly identified high-risk corridors '
                      'remains politically difficult when property values and tax revenues depend '
                      'on waterfront construction.',
                 'F': 'Insurance markets struggle to price rare catastrophic earthquakes fairly '
                      'while keeping coverage affordable for homeowners and small businesses near '
                      'active faults. Parametric policies triggered by instrumental intensity '
                      'reduce settlement delays, while traditional indemnity contracts face moral '
                      'hazard when owners postpone retrofits. Public catastrophe pools spread risk '
                      'nationally but may subsidise construction in known hazard zones if premiums '
                      'do not reflect site-specific geology. The author contends that pricing '
                      'signals should align with mitigation incentives, otherwise fiscal burdens '
                      'shift to taxpayers after each destructive season. Without actuarial '
                      'transparency, communities may underestimate true long-term costs of living '
                      'beside faults that remain quiet for generations between large events.',
                 'G': 'Looking ahead, integrating machine learning with physics-based rupture '
                      'models may sharpen short-term forecasts without abandoning mechanistic '
                      'understanding of fault physics. Open data initiatives encourage '
                      'universities and civil protection agencies to share catalogs, fostering '
                      'reproducible research and faster validation of new methods. The writer '
                      'believes societies can live more safely on active margins if science, '
                      'engineering, and governance co-evolve through regular dialogue and funding. '
                      'Seismic risk should be treated as a managed continuum rather than an '
                      'unpredictable curse that discourages prudent investment in monitoring '
                      'networks. Community education programmes that explain preparedness steps '
                      'can translate technical advances into everyday practices that save lives '
                      'when the ground finally shakes.'},
  'tfng': [{'question': 'Geodetic networks can detect crustal movement at millimetre scales.',
            'answer': 'True'},
           {'question': 'Every subduction zone has complete instrumental records spanning more '
                        'than five centuries.',
            'answer': 'False'},
           {'question': 'Paleoseismology always produces exact dates for the next earthquake.',
            'answer': 'False'},
           {'question': 'The passage states that all cities have completed masonry retrofits.',
            'answer': 'Not Given'},
           {'question': 'Submarine landslides may increase tsunami risk beyond magnitude-based '
                        'estimates.',
            'answer': 'True'}],
  'ynng': [{'question': 'The author prefers transparent communication of hazard uncertainty over '
                        'implying precise predictions.',
            'answer': 'Yes'},
           {'question': 'The writer believes early warning systems should fully replace '
                        'infrastructure investment.',
            'answer': 'No'},
           {'question': 'The author thinks insurance pricing should encourage mitigation rather '
                        'than hide true risk.',
            'answer': 'Yes'},
           {'question': 'The writer claims machine learning will make physics-based models '
                        'obsolete immediately.',
            'answer': 'No'},
           {'question': 'The author is optimistic that coordinated science and governance can '
                        'improve safety on active margins.',
            'answer': 'Yes'}],
  'matching_headings': [{'paragraph': 'B',
                         'correct': 'ii. Locked faults and extended rupture histories'},
                        {'paragraph': 'C',
                         'correct': 'iii. Hazard maps, site effects, and design codes'},
                        {'paragraph': 'D',
                         'correct': 'iv. Alerts from seismic wave timing differences'},
                        {'paragraph': 'E',
                         'correct': 'v. Inundation modelling and coastal rebuilding pressures'},
                        {'paragraph': 'F',
                         'correct': 'vi. Insurance pricing and catastrophe pools'}],
  'headings_pool': ['i. Volcanic ash fertilisation of high-latitude soils',
                    'j. Locked faults and extended rupture histories',
                    'k. Hazard maps, site effects, and design codes',
                    'l. Alerts from seismic wave timing differences',
                    'm. Inundation modelling and coastal rebuilding pressures',
                    'n. Insurance pricing and catastrophe pools',
                    'o. Lunar tidal forcing of mantle convection'],
  'matching_info': [{'question': 'a description of oceanic lithosphere descending beneath '
                                 'continents',
                     'paragraph': 'B'},
                    {'question': 'mention of performance-based building design', 'paragraph': 'C'},
                    {'question': 'reference to surgeons pausing during alerts', 'paragraph': 'D'},
                    {'question': 'discussion of bathymetry errors affecting inundation estimates',
                     'paragraph': 'E'},
                    {'question': 'a positive outlook on open data and reproducible research',
                     'paragraph': 'G'}],
  'sentence_completion': [{'question': 'Elastic energy accumulates along locked plate interfaces '
                                       'before sudden ____.',
                           'answer': 'ruptures'},
                          {'question': 'Attenuation relationships describe how shaking weakens '
                                       'with ____.',
                           'answer': 'distance'},
                          {'question': 'Early warnings exploit the lag between primary waves and '
                                       'destructive ____ waves.',
                           'answer': 'secondary'},
                          {'question': 'Parametric insurance policies may be triggered by '
                                       'instrumental ____.',
                           'answer': 'intensity'}],
  'summary_completion': [{'question': 'Plate motion is driven partly by mantle convection, slab '
                                      'pull, and ridge ____.',
                          'answer': 'push'},
                         {'question': 'Soft sedimentary basins beneath cities can amplify seismic '
                                      'site ____.',
                          'answer': 'effects'},
                         {'question': 'Tsunami simulations couple seafloor deformation with '
                                      'hydrodynamic ____.',
                          'answer': 'simulations'},
                         {'question': 'The author treats seismic risk as a managed ____.',
                          'answer': 'continuum'}],
  'table_completion': [{'question': 'Geodetic method | Networks track crustal strain at millimetre '
                                    '____',
                        'answer': 'scale'},
                       {'question': 'Warning limitation | False alarms can undermine public ____',
                        'answer': 'trust'},
                       {'question': 'Insurance issue | Moral hazard appears when owners delay ____',
                        'answer': 'retrofits'}],
  'mcq': [{'question': 'What does paragraph A emphasise about modern monitoring?',
           'options': ['It eliminates all tsunami risk.',
                       'It measures small-scale strain to refine forecasts.',
                       'It proves earthquakes are predictable to the day.',
                       'It replaces geological fieldwork entirely.'],
           'answer': 'It measures small-scale strain to refine forecasts.'},
          {'question': 'According to paragraph C, performance-based design focuses on',
           'options': ['uniform strength factors only',
                       'limiting collapse probability',
                       'banning construction near coasts',
                       'ignoring site effects'],
           'answer': 'limiting collapse probability'},
          {'question': 'Paragraph D indicates early warning systems',
           'options': ['replace evacuation planning',
                       'provide alerts seconds before strong shaking',
                       'predict earthquakes weeks in advance',
                       'operate without sensor networks'],
           'answer': 'provide alerts seconds before strong shaking'},
          {'question': 'Paragraph F suggests a problem with some catastrophe pools is that',
           'options': ['they forbid any insurance claims',
                       'premiums may not reflect site-specific geology',
                       'they only cover volcanic eruptions',
                       'they require machine learning expertise'],
           'answer': 'premiums may not reflect site-specific geology'},
          {'question': 'The final paragraph argues that better safety requires',
           'options': ['abandoning physics-based models',
                       'science, engineering, and governance working together',
                       'closing universities near fault lines',
                       'ending community education programmes'],
           'answer': 'science, engineering, and governance working together'}],
  'short_answer': [{'question': 'What satellite system helps estimate remaining fault slip?',
                    'answer': 'GNSS',
                    'word_limit': 1},
                   {'question': 'What geological method excavates coastal sediments for rupture '
                                'history?',
                    'answer': 'paleoseismology',
                    'word_limit': 1},
                   {'question': 'What fast seismic waves arrive before destructive shaking in '
                                'early warnings?',
                    'answer': 'primary',
                    'word_limit': 1},
                   {'question': 'What type of policies trigger payouts using instrumental '
                                'intensity?',
                    'answer': 'parametric',
                    'word_limit': 1}]},
 {'quiz_number': 5,
  'title': 'Marine microbiomes and ocean health',
  'topic_category': 'Science',
  'paragraphs': {'A': 'Marine microbiomes comprise bacteria, archaea, viruses, and microbial '
                      'eukaryotes that drive biogeochemical cycles across pelagic and benthic '
                      'habitats throughout the world ocean. Phytoplankton blooms export carbon to '
                      'depth while heterotrophic microbes remineralise organic matter, regulating '
                      'dissolved oxygen concentrations that fisheries and coastal communities '
                      'depend upon seasonally. Molecular surveys now reveal enormous diversity '
                      'invisible to microscopy, prompting researchers to treat the ocean as a '
                      'networked ecosystem rather than a passive dilution basin for terrestrial '
                      'pollutants. Rivers and atmospheric deposition deliver nutrients and '
                      'contaminants that reshape microbial metabolism near continental margins, '
                      'with consequences for climate feedbacks and public health along crowded '
                      'shorelines.',
                 'B': 'In sunlit surface waters, photosynthetic picocyanobacteria fix carbon '
                      'dioxide using trace metals that can become limiting when upstream inputs '
                      'change abruptly after storms or droughts. Viral lysis releases dissolved '
                      'organic carbon, short-circuiting classical food webs and altering gases '
                      'that influence cloud formation above the sea surface. Experiments with iron '
                      'enrichment stimulate blooms in high-nutrient low-chlorophyll regions, yet '
                      'ecological side effects remain difficult to predict across trophic levels. '
                      'The author cautions that geoengineering proposals must weigh carbon uptake '
                      'benefits against disruptions to fisheries and toxin-producing harmful algal '
                      'events near tourist coastlines. Cross-disciplinary collaboration, sustained '
                      'funding, and careful communication with affected communities remain central '
                      'to credible long-term outcomes.',
                 'C': 'Deep-sea sediments harbour slow-growing archaea that oxidise methane before '
                      'it reaches the water column, providing a biological buffer against '
                      'greenhouse gas release from hydrate deposits. Ocean warming may shrink this '
                      'microbial filter, amplifying positive feedback loops that accelerate '
                      'climate change unless emissions decline on land. Submersible sampling and '
                      'environmental DNA metabarcoding map communities around hydrothermal vents '
                      'and cold seeps exporting specialised enzymes useful for biotechnology. '
                      'Conservation planners argue that abyssal plains deserve protection from '
                      'mining claims until baseline microbiome functions are documented '
                      'comprehensively by international collaborations. Destroying poorly known '
                      'habitats for metals could erase evolutionary solutions to energy conversion '
                      'that laboratories have only begun to characterise.',
                 'D': 'Plastic particles adsorb persistent organic pollutants and transport '
                      'microbes across ocean basins, creating novel rafting communities on '
                      'drifting debris gathered by currents. Laboratory studies show biofilms '
                      'alter polymer breakdown rates, though field measurements remain sparse '
                      'across the major subtropical garbage accumulation zones. Policy debates '
                      'focus on source reduction upstream rather than ocean cleanup alone, because '
                      'fragmented microplastics continue entering food webs consumed by seabirds '
                      'and people. The writer believes circular economy measures on land will '
                      'deliver larger health gains than technologically unproven harvest devices '
                      'operating far from population centres. Without producer responsibility '
                      'laws, consumers bear visual pollution while manufacturers externalise '
                      'long-term ecological costs of disposable packaging.',
                 'E': 'Coral holobionts depend on symbiotic algae and bacterial consortia that '
                      'confer resistance to bleaching when thermal stress remains moderate and '
                      'water quality stays relatively stable. Probiotic treatments and assisted '
                      'evolution experiments attempt to bolster resilience, yet scaling '
                      'interventions across reef networks raises equity questions among nations. '
                      'Monitoring programmes combine autonomous gliders with satellite chlorophyll '
                      'imagery to detect anomalies early enough for managers to restrict anchoring '
                      'or runoff. Critics warn that microbiome manipulation could homogenise '
                      'diversity, whereas proponents see targeted interventions as a bridge while '
                      'global emissions decline slowly. Either way, reefs remain sentinels '
                      'demonstrating how microbial partnerships underpin macroscopic ecosystems '
                      'valued for tourism, fisheries, and coastal protection.',
                 'F': 'Fisheries managers seldom incorporate microbial indicators into stock '
                      'assessments, focusing instead on catch statistics and predator counts '
                      'compiled annually. Emerging metabarcoding of gut contents could reveal prey '
                      'shifts invisible to conventional surveys, improving ecosystem-based '
                      'management when funding permits. International data sharing remains uneven, '
                      'limiting models that link microbiome shifts to hypoxic dead zones expanding '
                      'under agricultural nutrient runoff. The author contends that funding '
                      'long-term observatories is cheaper than reacting to collapsed fisheries and '
                      'tourism revenue after sudden regime changes offshore. Invisible microbial '
                      'transitions often precede visible crashes, offering a window for '
                      'precautionary action if monitoring budgets survive political cycles.',
                 'G': 'Future research will integrate omics datasets with physical ocean models to '
                      'forecast tipping points in carbon export and oxygen minimum zones affecting '
                      'migratory species. Open science repositories can accelerate collaboration '
                      'if metadata standards harmonise across nations reluctant to share '
                      'proprietary cruise data. The writer maintains that respecting microbial '
                      'roles is essential for credible ocean health policy because invisible '
                      'communities regulate climate-relevant gases and nutrient recycling. '
                      'Education programmes translating metagenomics for fishers and city planners '
                      'may build support for ambitious protection targets debated at international '
                      'summits. Without public literacy, technical advances risk remaining '
                      'confined to journals while ecosystems degrade unnoticed until economic '
                      'losses become impossible to ignore.'},
  'tfng': [{'question': 'Phytoplankton blooms can transport carbon toward deeper water.',
            'answer': 'True'},
           {'question': 'Iron enrichment experiments never produce ecological side effects.',
            'answer': 'False'},
           {'question': 'All coral reefs have received large-scale probiotic treatments.',
            'answer': 'Not Given'},
           {'question': 'Archaea in sediments can oxidise methane before it escapes.',
            'answer': 'True'},
           {'question': 'The passage states every nation shares microbiome data equally.',
            'answer': 'Not Given'}],
  'ynng': [{'question': 'The author urges caution about ocean geoengineering proposals.',
            'answer': 'Yes'},
           {'question': 'The writer believes land-based circular economy measures outweigh distant '
                        'cleanup gadgets.',
            'answer': 'Yes'},
           {'question': 'The author thinks fisheries managers already fully use microbial '
                        'indicators.',
            'answer': 'No'},
           {'question': 'The writer claims probiotic reef treatments carry no equity concerns.',
            'answer': 'No'},
           {'question': 'The author sees long-term observatories as cost-effective prevention.',
            'answer': 'Yes'}],
  'matching_headings': [{'paragraph': 'B',
                         'correct': 'ii. Surface microbes, viruses, and nutrient experiments'},
                        {'paragraph': 'C',
                         'correct': 'iii. Methane oxidation and deep-sea sampling'},
                        {'paragraph': 'D',
                         'correct': 'iv. Plastics, biofilms, and upstream policy'},
                        {'paragraph': 'E',
                         'correct': 'v. Coral symbionts and resilience interventions'},
                        {'paragraph': 'F',
                         'correct': 'vi. Fisheries data gaps and shared monitoring'}],
  'headings_pool': ['i. Desert dust fertilisation of alpine lakes',
                    'j. Surface microbes, viruses, and nutrient experiments',
                    'k. Methane oxidation and deep-sea sampling',
                    'l. Plastics, biofilms, and upstream policy',
                    'm. Coral symbionts and resilience interventions',
                    'n. Fisheries data gaps and shared monitoring',
                    'o. Tidal turbine lubricant toxicity studies'],
  'matching_info': [{'question': 'mention of iron enrichment in high-nutrient low-chlorophyll '
                                 'regions',
                     'paragraph': 'B'},
                    {'question': 'reference to environmental DNA metabarcoding', 'paragraph': 'C'},
                    {'question': 'discussion of microplastics entering food webs',
                     'paragraph': 'D'},
                    {'question': 'examples of assisted evolution for reefs', 'paragraph': 'E'},
                    {'question': 'a conclusion about invisible communities regulating visible '
                                 'resources',
                     'paragraph': 'G'}],
  'sentence_completion': [{'question': 'Viral lysis releases dissolved organic ____ that alters '
                                       'food webs.',
                           'answer': 'carbon'},
                          {'question': 'Deep-sea archaea oxidise ____ before it reaches the water '
                                       'column.',
                           'answer': 'methane'},
                          {'question': 'Plastic particles can adsorb persistent organic ____.',
                           'answer': 'pollutants'},
                          {'question': 'Autonomous gliders help detect chlorophyll ____ early.',
                           'answer': 'anomalies'}],
  'summary_completion': [{'question': 'Picocyanobacteria fix carbon dioxide using trace ____.',
                          'answer': 'metals'},
                         {'question': 'Coral holobionts include symbiotic algae and bacterial '
                                      '____.',
                          'answer': 'consortia'},
                         {'question': 'Metabarcoding of gut contents may reveal prey ____.',
                          'answer': 'shifts'},
                         {'question': 'Open repositories need harmonised metadata ____.',
                          'answer': 'standards'}],
  'table_completion': [{'question': 'Surface process | Viral lysis short-circuits marine food ____',
                        'answer': 'webs'},
                       {'question': 'Deep buffer | Warming may shrink the microbial ____',
                        'answer': 'filter'},
                       {'question': 'Management gap | Stock assessments rarely use microbial ____',
                        'answer': 'indicators'}],
  'mcq': [{'question': 'What limitation does paragraph B note about iron enrichment?',
           'options': ['It only works in freshwater lakes.',
                       'Ecological side effects are hard to predict.',
                       'It eliminates harmful algal blooms entirely.',
                       'It requires no trace metals.'],
           'answer': 'Ecological side effects are hard to predict.'},
          {'question': 'Paragraph C suggests abyssal plains should be protected until',
           'options': ['all mining is banned globally',
                       'baseline microbiome functions are documented',
                       'every vent is mapped by tourists',
                       'plastic cleanup devices are deployed'],
           'answer': 'baseline microbiome functions are documented'},
          {'question': 'According to paragraph D, the writer prioritises',
           'options': ['ocean harvest gadgets over land policy',
                       'source reduction and circular economy measures',
                       'increasing microplastic production',
                       'ignoring biofilm research'],
           'answer': 'source reduction and circular economy measures'},
          {'question': 'Paragraph F indicates conventional fisheries surveys may miss',
           'options': ['predator counts entirely',
                       'prey shifts detectable via gut metabarcoding',
                       'any reference to catch statistics',
                       'oxygen concentrations'],
           'answer': 'prey shifts detectable via gut metabarcoding'},
          {'question': 'The final paragraph emphasises integrating',
           'options': ['omics data with physical ocean models',
                       'only satellite tourism imagery',
                       'microscopy alone without models',
                       'fisheries catch without metadata'],
           'answer': 'omics data with physical ocean models'}],
  'short_answer': [{'question': 'Which organisms fix carbon in sunlit surface waters?',
                    'answer': 'picocyanobacteria',
                    'word_limit': 1},
                   {'question': 'What gas do sediment archaea help prevent from reaching the water '
                                'column?',
                    'answer': 'methane',
                    'word_limit': 1},
                   {'question': 'What term describes the combined coral and its microbes?',
                    'answer': 'holobiont',
                    'word_limit': 1},
                   {'question': 'What expanding zones are linked to nutrient runoff in paragraph '
                                'F?',
                    'answer': 'dead zones',
                    'word_limit': 2}]},
 {'quiz_number': 6,
  'title': 'Vaccine adjuvants and immunity',
  'topic_category': 'Science',
  'paragraphs': {'A': 'Vaccine adjuvants are substances added to formulations to enhance immune '
                      'responses against antigens that might otherwise prove weakly immunogenic on '
                      'their own. Aluminium salts remain among the most widely deployed adjuvants, '
                      'stimulating local inflammation that recruits antigen-presenting cells to '
                      'lymph nodes. Novel platforms, including oil-in-water emulsions and '
                      'saponin-based matrices, aim to balance potency with tolerability across '
                      'diverse age groups and comorbidities. Regulators evaluate adjuvanted '
                      'products through extended safety monitoring because subtle autoimmune '
                      'signals may appear only after millions of doses are administered. '
                      'Understanding adjuvant mechanisms has become essential as developers pursue '
                      'vaccines against pathogens that evade conventional antibody responses.',
                 'B': 'Innate immune receptors recognise conserved molecular patterns on '
                      'adjuvants, triggering cytokine cascades that shape subsequent adaptive '
                      'immunity. Toll-like receptor agonists can bias responses toward cellular '
                      'immunity, which matters for intracellular pathogens and certain oncology '
                      'applications. Formulation science determines whether antigens remain at the '
                      'injection site or traffic efficiently to draining lymphoid tissue where T '
                      'cells are primed. Preclinical models using humanised mice and organoids '
                      'supplement traditional rodent studies, though translational gaps still '
                      'complicate dose selection for first-in-human trials. The author notes that '
                      'mechanistic clarity should guide design rather than empirical screening '
                      'alone, which historically produced effective but poorly understood '
                      'mixtures.',
                 'C': 'During recent pandemic deployments, adjuvanted dose-sparing strategies '
                      'stretched limited antigen supplies, enabling broader coverage in low-income '
                      'regions. Pharmacovigilance networks pooled reports of rare adverse events, '
                      'demonstrating both the value and the limits of global surveillance '
                      'infrastructure. Manufacturing adjuvants at scale requires stringent control '
                      'of lipid composition and endotoxin levels, because impurities can skew '
                      'immunogenicity unpredictably. Technology transfer agreements helped '
                      'regional producers adopt complex emulsion processes, yet quality audits '
                      'revealed uneven preparedness across facilities. The writer argues that '
                      'equitable access depends on sharing know-how, not merely shipping finished '
                      'vials that expire before cold chains reach remote clinics.',
                 'D': 'Personalised medicine aspirations extend to adjuvant selection based on '
                      'genetic polymorphisms affecting cytokine production and vaccine '
                      'reactogenicity. Biobanks linked to electronic health records could identify '
                      'subgroups benefiting from alternative formulations, though privacy '
                      'regulations complicate cross-border analysis. Critics caution against '
                      'over-interpreting early correlates of protection without confirmatory '
                      'efficacy trials spanning diverse populations. The author believes '
                      'stratified approaches may reduce public hesitancy if communicated '
                      'transparently rather than as opaque algorithmic recommendations. Ethical '
                      'review boards increasingly scrutinise whether adaptive trial designs '
                      'adequately protect participants offered experimental adjuvant combinations. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'E': 'Oncology vaccines employ adjuvants to break tolerance against '
                      'tumour-associated antigens, sometimes combining checkpoint inhibitors with '
                      'neoantigen peptides. Immune-related adverse events require oncology teams '
                      'to distinguish treatment toxicity from disease progression, delaying '
                      'therapy adjustments. Cost-effectiveness models weigh expensive personalised '
                      'adjuvant cocktails against standard chemotherapy regimens with established '
                      'reimbursement pathways. Regulators demand long-term follow-up for '
                      'therapeutic vaccines, extending trial timelines beyond those typical for '
                      'preventive infectious disease products. Despite hurdles, the writer sees '
                      'adjuvant innovation as a lever for durable cellular responses that '
                      'monoclonal antibodies alone cannot sustain indefinitely. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes.',
                 'F': 'Public communication about adjuvants frequently encounters misinformation '
                      'equating aluminium exposure from vaccines with environmental toxicity at '
                      'irrelevant doses. Scientists counter with pharmacokinetic data showing '
                      'local deposition and gradual clearance, yet narrative framing on social '
                      'media often overwhelms nuanced explanations. School-based education and '
                      'clinician training materials are being revised to address adjuvant '
                      'questions without dismissing legitimate concerns about transparency. The '
                      'author contends that respectful dialogue outperforms punitive content '
                      'moderation when building trust among communities historically underserved '
                      'by research. Without trust, even optimally formulated adjuvants cannot '
                      'fulfil their public health promise during outbreaks requiring rapid mass '
                      'immunisation.',
                 'G': 'Future adjuvant research will likely integrate systems immunology models '
                      'predicting human responses from high-dimensional blood profiling after '
                      'early doses. Open-access databases of adjuvant structures and trial '
                      'outcomes could reduce redundant experimentation if sponsors overcome '
                      'proprietary instincts. The writer maintains that adjuvants are not mere '
                      'additives but co-determinants of vaccine success, deserving parity with '
                      'antigen discovery in funding portfolios. International harmonisation of '
                      'approval standards may accelerate introduction of next-generation platforms '
                      'while preserving rigorous safety thresholds. If discovery, manufacturing, '
                      'and communication advance together, societies may respond more confidently '
                      'when novel pathogens inevitably emerge. Cross-disciplinary collaboration, '
                      'sustained funding, and careful communication with affected communities '
                      'remain central to credible long-term outcomes.'},
  'tfng': [{'question': 'Aluminium salts are among widely used vaccine adjuvants.',
            'answer': 'True'},
           {'question': 'All adjuvants have been fully mechanistically understood for decades.',
            'answer': 'False'},
           {'question': 'The passage states every oncology vaccine has received reimbursement '
                        'globally.',
            'answer': 'Not Given'},
           {'question': 'Toll-like receptor agonists can influence cellular immune bias.',
            'answer': 'True'},
           {'question': 'Adjuvanted dose-sparing was used during recent pandemic deployments.',
            'answer': 'True'}],
  'ynng': [{'question': 'The author prefers mechanistic design over purely empirical adjuvant '
                        'screening.',
            'answer': 'Yes'},
           {'question': 'The writer believes shipping vials alone ensures equitable access.',
            'answer': 'No'},
           {'question': 'The author thinks transparent communication may reduce vaccine hesitancy.',
            'answer': 'Yes'},
           {'question': 'The writer claims punitive moderation is always the best trust-building '
                        'tool.',
            'answer': 'No'},
           {'question': 'The author sees adjuvants as co-determinants of vaccine success.',
            'answer': 'Yes'}],
  'matching_headings': [{'paragraph': 'B',
                         'correct': 'ii. Innate receptors and formulation science'},
                        {'paragraph': 'C',
                         'correct': 'iii. Pandemic dose-sparing and manufacturing quality'},
                        {'paragraph': 'D',
                         'correct': 'iv. Genetic stratification and ethical trial design'},
                        {'paragraph': 'E', 'correct': 'v. Therapeutic vaccines in oncology'},
                        {'paragraph': 'F', 'correct': 'vi. Misinformation and public trust'}],
  'headings_pool': ['i. Herbal supplement marketing regulations',
                    'j. Innate receptors and formulation science',
                    'k. Pandemic dose-sparing and manufacturing quality',
                    'l. Genetic stratification and ethical trial design',
                    'm. Therapeutic vaccines in oncology',
                    'n. Misinformation and public trust',
                    'o. Deep-sea sponge aquaculture'],
  'matching_info': [{'question': 'discussion of toll-like receptor agonists', 'paragraph': 'B'},
                    {'question': 'mention of technology transfer for emulsion manufacturing',
                     'paragraph': 'C'},
                    {'question': 'reference to biobanks and electronic health records',
                     'paragraph': 'D'},
                    {'question': 'examples of checkpoint inhibitors with neoantigen peptides',
                     'paragraph': 'E'},
                    {'question': 'a forward-looking view of systems immunology models',
                     'paragraph': 'G'}],
  'sentence_completion': [{'question': 'Adjuvants recruit antigen-presenting cells to lymph ____.',
                           'answer': 'nodes'},
                          {'question': 'Oil-in-water emulsions aim to balance potency with ____.',
                           'answer': 'tolerability'},
                          {'question': 'Pharmacovigilance networks pooled reports of rare adverse '
                                       '____.',
                           'answer': 'events'},
                          {'question': 'Open databases could reduce redundant ____.',
                           'answer': 'experimentation'}],
  'summary_completion': [{'question': 'Aluminium salts stimulate local ____ that recruits immune '
                                      'cells.',
                          'answer': 'inflammation'},
                         {'question': 'Dose-sparing strategies stretched limited antigen supplies '
                                      'in low-income ____.',
                          'answer': 'regions'},
                         {'question': 'Oncology teams must distinguish toxicity from disease ____.',
                          'answer': 'progression'},
                         {'question': 'International harmonisation may preserve rigorous safety '
                                      '____.',
                          'answer': 'thresholds'}],
  'table_completion': [{'question': 'Innate pathway | Adjuvants trigger cytokine ____',
                        'answer': 'cascades'},
                       {'question': 'Manufacturing | Impurities such as endotoxin skew ____.',
                        'answer': 'immunogenicity'},
                       {'question': 'Communication | Misinformation links aluminium to irrelevant '
                                    'environmental ____.',
                        'answer': 'toxicity'}],
  'mcq': [{'question': 'Paragraph A indicates adjuvants are used because some antigens are',
           'options': ['always toxic',
                       'weakly immunogenic alone',
                       'illegal without oil emulsions',
                       'only effective in mice'],
           'answer': 'weakly immunogenic alone'},
          {'question': 'According to paragraph C, equitable access requires',
           'options': ['banning regional manufacturing',
                       'sharing manufacturing know-how',
                       'eliminating cold chains',
                       'avoiding pharmacovigilance'],
           'answer': 'sharing manufacturing know-how'},
          {'question': 'Paragraph E suggests oncology adjuvant trials face',
           'options': ['shorter follow-up than preventive vaccines',
                       'longer follow-up than many preventive products',
                       'no immune-related adverse events',
                       'automatic reimbursement'],
           'answer': 'longer follow-up than many preventive products'},
          {'question': 'Paragraph F indicates social media often',
           'options': ['amplifies nuanced pharmacokinetic explanations',
                       'overwhelms nuanced scientific explanations',
                       'eliminates all vaccine hesitancy',
                       'replaces clinician training'],
           'answer': 'overwhelms nuanced scientific explanations'},
          {'question': 'The final paragraph argues adjuvants deserve',
           'options': ['less funding than antigens',
                       'parity with antigen discovery in funding',
                       'no international standards',
                       'only empirical screening'],
           'answer': 'parity with antigen discovery in funding'}],
  'short_answer': [{'question': 'Which salts are named as widely deployed adjuvants?',
                    'answer': 'aluminium',
                    'word_limit': 1},
                   {'question': 'What receptor class recognises molecular patterns on adjuvants?',
                    'answer': 'Toll-like',
                    'word_limit': 2},
                   {'question': 'What strategy stretched antigen supplies during pandemics?',
                    'answer': 'dose-sparing',
                    'word_limit': 1},
                   {'question': 'What inhibitors are combined with neoantigen peptides in '
                                'oncology?',
                    'answer': 'checkpoint',
                    'word_limit': 1}]},
 {'quiz_number': 7,
  'title': 'Nanomaterials in targeted medicine',
  'topic_category': 'Science',
  'paragraphs': {'A': 'Nanomaterials enable drug carriers, imaging agents, and scaffolds sized at '
                      'scales where surface area dominates bulk properties, altering '
                      'biodistribution and cellular uptake. Lipid nanoparticles gained prominence '
                      'delivering fragile nucleic acid therapies that degrade rapidly in '
                      'bloodstream without protective encapsulation. Surface functionalisation '
                      'with antibodies or peptides can direct particles toward tumours expressing '
                      'specific receptors, though heterogeneity limits uniform targeting. '
                      'Regulators classify many products as combination devices requiring evidence '
                      'on manufacturing reproducibility, sterility, and long-term biodegradation '
                      'profiles. Clinical translation depends on balancing enhanced efficacy '
                      'against unknown chronic accumulation in liver, spleen, and other '
                      'mononuclear phagocyte reservoirs. Cross-disciplinary collaboration, '
                      'sustained funding, and careful communication with affected communities '
                      'remain central to credible long-term outcomes.',
                 'B': 'Engineers tune particle size and charge to evade opsonisation while '
                      'promoting endosomal escape after internalisation by target cells. Gold and '
                      'iron oxide cores provide contrast for magnetic resonance imaging, guiding '
                      'surgeons toward margins invisible to palpation alone. Computational models '
                      'simulate blood flow and margination near vessel walls, informing design '
                      'choices before expensive animal studies commence. The author emphasises '
                      'that in silico pipelines must be validated experimentally because patient '
                      'vasculature varies with age, inflammation, and comorbidities. Standardised '
                      'characterisation methods measuring polydispersity and zeta potential remain '
                      'essential when scaling batch production from milligrams to kilograms. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'C': 'Toxicology studies examine whether degradation products trigger oxidative '
                      'stress or complement activation after repeated dosing schedules. '
                      'Biodistribution imaging with radiolabelled tracers reveals off-target '
                      'accumulation in kidneys and bone marrow that might not appear in short '
                      'acute studies. Regulatory agencies request carcinogenicity assessments for '
                      'persistent inorganic cores even when therapeutic benefits appear '
                      'substantial in early trials. Patient advocacy groups demand plain-language '
                      'summaries explaining unknown long-term risks, especially for paediatric '
                      'oncology indications. The writer argues transparent uncertainty disclosure '
                      'builds trust more effectively than marketing claims implying nanoscale '
                      'magic without mechanistic evidence. Cross-disciplinary collaboration, '
                      'sustained funding, and careful communication with affected communities '
                      'remain central to credible long-term outcomes.',
                 'D': 'Manufacturing nanomedicines requires cleanroom environments controlling '
                      'particulate contamination that could nucleate unstable aggregates. '
                      'Microfluidic platforms improve batch consistency by mixing lipids under '
                      'laminar flow conditions difficult to reproduce in stirred vessels. Supply '
                      'chain disruptions for specialised lipids during global health emergencies '
                      'exposed dependence on few international suppliers. Technology transfer to '
                      'regional producers must include analytical method packages, not merely '
                      'equipment installation manuals. The author contends decentralised '
                      'production could improve outbreak response if quality systems receive '
                      'sustained investment rather than temporary grants. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes.',
                 'E': 'Personalised nanocarriers loading patient-specific neoantigens represent an '
                      'ambitious frontier coupling immunology with precision engineering. '
                      'Autologous manufacturing timelines may exceed tumour progression windows '
                      'unless modular platforms accelerate formulation within days. Reimbursement '
                      'agencies question whether incremental survival gains justify six-figure '
                      'costs per course compared with checkpoint inhibitors alone. Ethicists '
                      'debate whether resource-intensive personalised nanomedicines widen '
                      'disparities between wealthy hospitals and public systems. Despite equity '
                      'concerns, the writer believes iterative cost reduction through automation '
                      'could eventually democratise access if patents expire responsibly. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'F': 'Environmental release of nanoparticles from medical waste incineration and '
                      'wastewater has prompted lifecycle assessments beyond clinic walls. '
                      'Ecotoxicologists document subtle effects on aquatic invertebrates at '
                      'concentrations far below those used therapeutically, complicating disposal '
                      'regulations. Hospitals explore filtration upgrades and take-back programmes '
                      'for unused vials to minimise environmental loading. Industry consortia '
                      'propose labelling standards identifying persistent inorganic content for '
                      'waste handlers. The author maintains that therapeutic innovation must '
                      'include end-of-life planning, otherwise nanomedicine exports hidden '
                      'externalities to communities downstream. Cross-disciplinary collaboration, '
                      'sustained funding, and careful communication with affected communities '
                      'remain central to credible long-term outcomes. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes.',
                 'G': 'Looking ahead, smart nanoparticles responding to tumour microenvironment '
                      'cues may release payloads only upon encountering acidic or enzymatic '
                      'triggers. Closed-loop imaging could confirm activation before surgeons '
                      'proceed, reducing damage to healthy tissue. International collaboration on '
                      'reference materials will help compare studies using incompatible '
                      'measurement techniques. The writer foresees nanomedicine maturing into a '
                      'disciplined field when regulators, engineers, and clinicians share datasets '
                      'openly. Such integration could transform targeted therapy from headline '
                      'novelty into routine practice governed by evidence rather than speculation. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.'},
  'tfng': [{'question': 'Lipid nanoparticles help protect nucleic acid therapies in blood.',
            'answer': 'True'},
           {'question': 'Every tumour expresses uniform receptor targets for nanoparticles.',
            'answer': 'False'},
           {'question': 'The passage states all paediatric trials have concluded with ten-year '
                        'follow-up.',
            'answer': 'Not Given'},
           {'question': 'Microfluidic mixing can improve batch consistency.', 'answer': 'True'},
           {'question': 'Gold cores can provide magnetic resonance contrast.', 'answer': 'True'}],
  'ynng': [{'question': 'The author insists in silico models need experimental validation.',
            'answer': 'Yes'},
           {'question': 'The writer believes marketing should hide long-term uncertainty.',
            'answer': 'No'},
           {'question': 'The author supports transparent uncertainty disclosure for patients.',
            'answer': 'Yes'},
           {'question': 'The writer claims personalised nanomedicines can never become affordable.',
            'answer': 'No'},
           {'question': 'The author wants end-of-life environmental planning included in '
                        'innovation.',
            'answer': 'Yes'}],
  'matching_headings': [{'paragraph': 'B', 'correct': 'ii. Engineering uptake and imaging cores'},
                        {'paragraph': 'C', 'correct': 'iii. Toxicology and regulatory uncertainty'},
                        {'paragraph': 'D',
                         'correct': 'iv. Cleanroom manufacturing and supply chains'},
                        {'paragraph': 'E',
                         'correct': 'v. Personalised carriers and equity debates'},
                        {'paragraph': 'F',
                         'correct': 'vi. Environmental release and waste planning'}],
  'headings_pool': ['i. Volcanic glass cosmetics marketing',
                    'j. Engineering uptake and imaging cores',
                    'k. Toxicology and regulatory uncertainty',
                    'l. Cleanroom manufacturing and supply chains',
                    'm. Personalised carriers and equity debates',
                    'n. Environmental release and waste planning',
                    'o. Antarctic krill fishing quotas'],
  'matching_info': [{'question': 'discussion of endosomal escape after internalisation',
                     'paragraph': 'B'},
                    {'question': 'reference to radiolabelled biodistribution imaging',
                     'paragraph': 'C'},
                    {'question': 'mention of microfluidic lipid mixing', 'paragraph': 'D'},
                    {'question': 'debate about six-figure treatment costs', 'paragraph': 'E'},
                    {'question': 'vision of environment-triggered smart nanoparticles',
                     'paragraph': 'G'}],
  'sentence_completion': [{'question': 'Surface functionalisation can direct particles using '
                                       'antibodies or ____.',
                           'answer': 'peptides'},
                          {'question': 'Zeta potential helps characterise particle ____ during '
                                       'scale-up.',
                           'answer': 'stability'},
                          {'question': 'Tumour microenvironment triggers may include acidic or '
                                       '____ cues.',
                           'answer': 'enzymatic'},
                          {'question': 'Hospitals explore filtration upgrades for medical ____.',
                           'answer': 'wastewater'}],
  'summary_completion': [{'question': 'Opsonisation affects how particles are cleared by immune '
                                      '____.',
                          'answer': 'cells'},
                         {'question': 'Regional producers need analytical method packages during '
                                      'technology ____.',
                          'answer': 'transfer'},
                         {'question': 'Lifecycle assessments consider incineration and ____ '
                                      'release.',
                          'answer': 'wastewater'},
                         {'question': 'Reference materials could reduce incompatible measurement '
                                      '____.',
                          'answer': 'techniques'}],
  'table_completion': [{'question': 'Design tool | Computational models simulate blood ____',
                        'answer': 'flow'},
                       {'question': 'Toxicology | Persistent cores may require carcinogenicity '
                                    '____',
                        'answer': 'assessments'},
                       {'question': 'Future therapy | Closed-loop imaging confirms payload ____',
                        'answer': 'activation'}],
  'mcq': [{'question': 'Paragraph A suggests nanomaterials are valuable because',
           'options': ['they ignore surface properties',
                       'surface area alters uptake and distribution',
                       'they eliminate regulatory review',
                       'they work only without encapsulation'],
           'answer': 'surface area alters uptake and distribution'},
          {'question': 'According to paragraph D, global emergencies revealed',
           'options': ['unlimited lipid suppliers worldwide',
                       'dependence on few specialised suppliers',
                       'no need for cleanrooms',
                       'ban on technology transfer'],
           'answer': 'dependence on few specialised suppliers'},
          {'question': 'Paragraph E indicates reimbursement debates focus on',
           'options': ['cost versus incremental survival gains',
                       'eliminating checkpoint inhibitors',
                       'mandatory six-figure pricing',
                       'aquatic invertebrates'],
           'answer': 'cost versus incremental survival gains'},
          {'question': 'Paragraph F discusses environmental effects on',
           'options': ['only hospital administrators',
                       'aquatic invertebrates at low concentrations',
                       'therapeutic doses in clinics',
                       'magnetic resonance machines'],
           'answer': 'aquatic invertebrates at low concentrations'},
          {'question': 'The final paragraph predicts maturation when',
           'options': ['datasets are shared openly across disciplines',
                       'marketing replaces evidence',
                       'regulators stop reviewing devices',
                       'imaging is abandoned'],
           'answer': 'datasets are shared openly across disciplines'}],
  'short_answer': [{'question': 'What nanoparticle type is named for nucleic acid delivery?',
                    'answer': 'lipid',
                    'word_limit': 1},
                   {'question': 'What property besides size is measured with zeta potential?',
                    'answer': 'charge',
                    'word_limit': 1},
                   {'question': 'What organs commonly accumulate nanoparticles according to '
                                'paragraph A?',
                    'answer': 'liver',
                    'word_limit': 1},
                   {'question': 'What term describes manufacturing tailored to individual tumours?',
                    'answer': 'personalised',
                    'word_limit': 1}]},
 {'quiz_number': 8,
  'title': 'Ocean acidification and shellfish',
  'topic_category': 'Environment',
  'paragraphs': {'A': 'Ocean acidification arises as seawater absorbs anthropogenic carbon '
                      'dioxide, lowering pH and reducing carbonate ion availability essential for '
                      'calcifying organisms. Shellfish aquaculture depends on larvae producing '
                      'fragile shells during early development stages highly sensitive to chemical '
                      'saturation states. Coastal upwelling regions naturally experience corrosive '
                      'waters, offering previews of conditions spreading under continued emissions '
                      'trajectories. Farmers monitor hatchery intake chemistry, adjusting rearing '
                      'protocols when aragonite saturation falls below thresholds linked to '
                      'developmental deformities. Scientists collaborate with industry because '
                      'economic losses appear years before open-ocean changes become obvious to '
                      'casual observers. Cross-disciplinary collaboration, sustained funding, and '
                      'careful communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'B': 'Biological impacts extend beyond shell formation to altered behaviour, '
                      'metabolism, and immune competence in adult bivalves and crustaceans. '
                      'Experiments in controlled flumes manipulate pH while holding temperature '
                      'constant, isolating acidification effects from concurrent warming '
                      'stressors. Field studies along volcanic carbon dioxide seeps document '
                      'community shifts toward non-calcifying species dominating seafloor biomass. '
                      'Restoration ecologists worry that weakened shellfish beds provide less '
                      'coastal protection from storm surges as reefs and marshes degrade '
                      'simultaneously. The author cautions against treating acidification as a '
                      'distant open-ocean issue irrelevant to nearshore livelihoods and food '
                      'security. Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'C': 'Mitigation at hatcheries includes buffering intake water with carbonate '
                      'minerals or deploying electrochemical systems that strip carbon dioxide. '
                      'These interventions raise energy and material costs, prompting cooperatives '
                      'to share monitoring equipment and technical advisers. Selective breeding '
                      'programmes identify broodstock families tolerating lower saturation, though '
                      'genetic gains must not compromise disease resistance. Policy incentives for '
                      'low-carbon energy at processing plants indirectly benefit growers facing '
                      'acidification alongside fuel price volatility. The writer believes local '
                      'adaptation tools buy time but cannot replace aggressive emissions '
                      'reductions on land. Cross-disciplinary collaboration, sustained funding, '
                      'and careful communication with affected communities remain central to '
                      'credible long-term outcomes.',
                 'D': 'Regional fisheries management councils increasingly request acidification '
                      'projections when setting harvest quotas for culturally important species. '
                      'Indigenous nations dependent on clam gardens argue that treaty rights '
                      'should trigger government funding for hatchery upgrades. Legal scholars '
                      'examine whether failure to curb emissions constitutes negligence toward '
                      'communities whose economies rely on shellfish exports. International '
                      'climate negotiations seldom mention aquaculture explicitly, leaving '
                      'sectoral advocates to translate global temperature targets into chemical '
                      'endpoints. The author contends that justice frameworks must connect '
                      'atmospheric policy with shoreline consequences visible in empty nursery '
                      'tanks. Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'E': 'Research networks deploy autonomous buoys measuring pH, temperature, and '
                      'salinity, transmitting alerts when corrosive events approach farms. Machine '
                      'learning models fuse buoy data with satellite chlorophyll to forecast '
                      'harmful synergies between acidification and algal toxins. Data sharing '
                      'agreements between competing companies remain rare, limiting ensemble '
                      'forecasts that could protect entire bays. Open platforms sponsored by '
                      'universities may overcome commercial secrecy if anonymisation protects '
                      'proprietary site locations adequately. The writer supports collaborative '
                      'forecasting because isolated farms cannot outrun regional chemistry shifts '
                      'driven by basin-scale processes. Cross-disciplinary collaboration, '
                      'sustained funding, and careful communication with affected communities '
                      'remain central to credible long-term outcomes.',
                 'F': 'Consumer education campaigns describe how sustainable aquaculture practices '
                      'differ from wild harvest stressed by multiple stressors. Certification '
                      'schemes add acidification vulnerability indices, though shoppers struggle '
                      'to interpret labels without contextual storytelling. Restaurants partnering '
                      'with scientists host tasting events featuring resilient strains, linking '
                      'culinary culture to conservation narratives. Critics argue market-based '
                      'certification inadequately addresses root causes requiring legislative '
                      'carbon pricing. The author believes cultural engagement complements '
                      'regulation, transforming shellfish from commodity statistics into symbols '
                      'motivating climate action. Cross-disciplinary collaboration, sustained '
                      'funding, and careful communication with affected communities remain central '
                      'to credible long-term outcomes. Policymakers increasingly demand '
                      'reproducible evidence, open data, and independent evaluation before scaling '
                      'interventions beyond controlled pilot settings.',
                 'G': 'Future scenarios hinge on whether nations meet emissions pathways limiting '
                      'surface pH decline this century. Geoengineering proposals to alkalinise '
                      'oceans raise ecological risks and governance questions far exceeding '
                      'hatchery-scale buffering. Integrated coastal zone plans may relocate '
                      'vulnerable farms inland or toward species less dependent on carbonate '
                      'skeletons. The writer maintains that shellfish farmers are frontline '
                      'observers whose monitoring data should inform national climate assessments. '
                      'Recognising their testimony could align adaptation funding with communities '
                      'already investing private capital in chemical resilience. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.'},
  'tfng': [{'question': 'Ocean acidification is linked to seawater absorbing carbon dioxide.',
            'answer': 'True'},
           {'question': 'Adult shellfish are never affected by acidification according to the '
                        'passage.',
            'answer': 'False'},
           {'question': 'Every nation has funded hatchery upgrades through treaty litigation.',
            'answer': 'Not Given'},
           {'question': 'Volcanic seeps help study community shifts under high carbon dioxide.',
            'answer': 'True'},
           {'question': 'Geoengineering alkalinisation is presented as risk-free.',
            'answer': 'False'}],
  'ynng': [{'question': 'The author says hatchery tools cannot replace emissions reductions.',
            'answer': 'Yes'},
           {'question': 'The writer believes acidification is irrelevant to nearshore livelihoods.',
            'answer': 'No'},
           {'question': 'The author connects justice frameworks to shoreline economic impacts.',
            'answer': 'Yes'},
           {'question': 'The writer thinks certification alone solves root causes without carbon '
                        'pricing.',
            'answer': 'No'},
           {'question': 'The author values shellfish farmers as frontline climate observers.',
            'answer': 'Yes'}],
  'matching_headings': [{'paragraph': 'B',
                         'correct': 'ii. Biological effects beyond shell formation'},
                        {'paragraph': 'C',
                         'correct': 'iii. Hatchery buffering and selective breeding'},
                        {'paragraph': 'D',
                         'correct': 'iv. Treaty rights and legal negligence debates'},
                        {'paragraph': 'E', 'correct': 'v. Buoys, forecasting, and data sharing'},
                        {'paragraph': 'F',
                         'correct': 'vi. Certification, culture, and consumer education'}],
  'headings_pool': ['i. Alpine skiing snowmaking economics',
                    'j. Biological effects beyond shell formation',
                    'k. Hatchery buffering and selective breeding',
                    'l. Treaty rights and legal negligence debates',
                    'm. Buoys, forecasting, and data sharing',
                    'n. Certification, culture, and consumer education',
                    'o. Mars rover wheel design'],
  'matching_info': [{'question': 'experiments isolating pH effects in controlled flumes',
                     'paragraph': 'B'},
                    {'question': 'mention of carbonate mineral buffering at hatcheries',
                     'paragraph': 'C'},
                    {'question': 'discussion of clam gardens and treaty rights', 'paragraph': 'D'},
                    {'question': 'reference to machine learning with buoy data', 'paragraph': 'E'},
                    {'question': 'a conclusion about farmers informing national assessments',
                     'paragraph': 'G'}],
  'sentence_completion': [{'question': 'Lower pH reduces carbonate ion availability for ____ '
                                       'organisms.',
                           'answer': 'calcifying'},
                          {'question': 'Farmers adjust rearing protocols when aragonite ____ falls '
                                       'below thresholds.',
                           'answer': 'saturation'},
                          {'question': 'Autonomous buoys measure pH, temperature, and ____.',
                           'answer': 'salinity'},
                          {'question': 'Selective breeding seeks broodstock tolerating lower ____.',
                           'answer': 'saturation'}],
  'summary_completion': [{'question': 'Larvae produce fragile shells during early ____ stages.',
                          'answer': 'development'},
                         {'question': 'Upwelling regions offer previews of spreading chemical '
                                      '____.',
                          'answer': 'conditions'},
                         {'question': 'Legal scholars ask whether emission failure constitutes '
                                      '____.',
                          'answer': 'negligence'},
                         {'question': 'Integrated plans may relocate farms toward less '
                                      'carbonate-dependent ____.',
                          'answer': 'species'}],
  'table_completion': [{'question': 'Stress factor | Concurrent warming complicates acidification '
                                    '____',
                        'answer': 'studies'},
                       {'question': 'Mitigation | Electrochemical systems strip carbon ____',
                        'answer': 'dioxide'},
                       {'question': 'Market tool | Certification adds vulnerability ____',
                        'answer': 'indices'}],
  'mcq': [{'question': 'Paragraph A emphasises shellfish aquaculture vulnerability during',
           'options': ['adult harvesting only',
                       'larval shell formation stages',
                       'deep-sea mining',
                       'forest clearance'],
           'answer': 'larval shell formation stages'},
          {'question': 'According to paragraph C, selective breeding must avoid compromising',
           'options': ['shell colour', 'disease resistance', 'water salinity', 'boat fuel use'],
           'answer': 'disease resistance'},
          {'question': 'Paragraph E suggests regional forecasts are limited because',
           'options': ['buoys are illegal',
                       'data sharing among competitors is rare',
                       'chlorophyll cannot be measured',
                       'universities ban anonymisation'],
           'answer': 'data sharing among competitors is rare'},
          {'question': 'Paragraph F indicates critics view certification as',
           'options': ['fully solving root causes',
                       'inadequate without legislative carbon pricing',
                       'unnecessary for restaurants',
                       'superior to cultural engagement'],
           'answer': 'inadequate without legislative carbon pricing'},
          {'question': 'The final paragraph urges using farmer data in',
           'options': ['national climate assessments',
                       'volcanic geoengineering only',
                       'wild harvest bans',
                       'consumer label removal'],
           'answer': 'national climate assessments'}],
  'short_answer': [{'question': 'What ion availability declines as oceans acidify?',
                    'answer': 'carbonate',
                    'word_limit': 1},
                   {'question': 'What natural coastal feature previews corrosive waters?',
                    'answer': 'upwelling',
                    'word_limit': 1},
                   {'question': 'What mineral is used to buffer hatchery intake water?',
                    'answer': 'carbonate',
                    'word_limit': 1},
                   {'question': 'What gardens are mentioned in relation to Indigenous nations?',
                    'answer': 'clam',
                    'word_limit': 1}]},
 {'quiz_number': 9,
  'title': 'Sleep and memory consolidation',
  'topic_category': 'Psychology',
  'paragraphs': {'A': 'Sleep supports memory consolidation through coordinated oscillations across '
                      'hippocampal and neocortical networks that replay daytime experiences. '
                      'Slow-wave sleep appears particularly important for stabilising declarative '
                      'memories, whereas rapid eye movement sleep associates with emotional and '
                      'procedural learning. Laboratory studies depriving participants of specific '
                      'sleep stages reveal selective deficits on recall tasks administered after '
                      'recovery nights. Neuroimaging tracks reactivation patterns suggesting the '
                      'brain prioritises salient or unfinished learning during offline processing. '
                      'Educational policymakers increasingly question whether early school start '
                      'times undermine adolescent learning by truncating sleep opportunity. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'B': 'Synaptic homeostasis theories propose that sleep downscales net synaptic '
                      'strength, preventing saturation while preserving relative connection '
                      'weights encoding memories. Pharmacological agents modulating GABAergic tone '
                      'can alter slow oscillation amplitude, offering experimental tools but '
                      'raising safety concerns for healthy volunteers. Animal models using '
                      'optogenetics trigger replay on demand, strengthening causal links between '
                      'neural sequences and behavioural performance improvements. The author warns '
                      'against oversimplifying sleep as a passive storage period; active selection '
                      'mechanisms may discard irrelevant details intentionally. Such nuance '
                      'complicates commercial apps promising universal memory boosts through '
                      'generic audio tracks played during sleep. Cross-disciplinary collaboration, '
                      'sustained funding, and careful communication with affected communities '
                      'remain central to credible long-term outcomes.',
                 'C': 'Clinical populations with insomnia, sleep apnoea, or shift-work disorder '
                      'show inconsistent memory profiles, complicating generalisations from '
                      'healthy cohorts. Treating apnoea with positive airway pressure sometimes '
                      'improves delayed recall, suggesting reversible components of cognitive '
                      'impairment. Longitudinal ageing studies associate chronic short sleep with '
                      'faster accumulation of biomarkers linked to neurodegeneration, though '
                      'causality remains debated. Public health campaigns promote sleep hygiene, '
                      'yet structural factors like housing noise and economic precarity limit '
                      'individual control. The writer argues interventions must address '
                      'environmental determinants rather than blaming students or workers for '
                      'societal scheduling choices. Cross-disciplinary collaboration, sustained '
                      'funding, and careful communication with affected communities remain central '
                      'to credible long-term outcomes.',
                 'D': 'Educational experiments delaying school bells report improved attendance '
                      'and standardised test scores in districts willing to adjust transport '
                      'logistics. Teachers note better classroom engagement, although curriculum '
                      'pacing pressures sometimes offset gains when instructional minutes remain '
                      'fixed. Universities experimenting with later exam slots observe fewer '
                      'careless errors attributed to sleepiness, yet sports training schedules '
                      'conflict. Employers piloting flexible start times report mixed productivity '
                      'outcomes depending on industry and coordination requirements across teams. '
                      'The author contends that aligning institutions with circadian science is a '
                      'low-cost reform compared with expensive remedial tutoring programmes. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'E': 'Technology use before bedtime receives blame for sleep curtailment, though '
                      'evidence distinguishes passive reading on e-paper from stimulating social '
                      'media. Blue-light filtering settings produce modest melatonin effects in '
                      'controlled trials, smaller than the impact of content emotional arousal. '
                      'Wearable trackers quantify sleep duration yet accuracy varies, risking '
                      'anxiety when users obsess over imperfect stage classifications. Clinicians '
                      'worry that orthosomnia leads patients to misinterpret benign night '
                      'awakenings as pathology requiring unnecessary medication. The writer '
                      'recommends interpreting consumer sleep data cautiously while designing '
                      'studies using research-grade polysomnography when possible. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'F': 'Memory research informs legal debates about eyewitness reliability after '
                      'sleep-deprived identifications during lengthy investigations. Forensic '
                      'psychologists caution juries that fatigue may distort confidence without '
                      'reducing subjective certainty felt by witnesses. Policy proposals limit '
                      'consecutive interrogation hours, citing sleep science alongside human '
                      'rights protections. Defence attorneys introduce expert testimony '
                      'summarising consolidation literature, though judges apply admissibility '
                      'standards unevenly. The author believes justice systems should incorporate '
                      'sleep evidence without deterministic claims that fatigue always invalidates '
                      'testimony. Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes. Policymakers increasingly demand reproducible evidence, '
                      'open data, and independent evaluation before scaling interventions beyond '
                      'controlled pilot settings.',
                 'G': 'Future work may personalise sleep recommendations using genetic chronotype '
                      'markers and real-world light exposure sensors. Ethical safeguards must '
                      'prevent employers from penalising workers classified as night owls through '
                      'invasive monitoring. Open datasets linking sleep architecture to learning '
                      'outcomes could guide adaptive educational software pacing review sessions. '
                      'The writer maintains sleep is a public good intersecting cognition, health, '
                      'and equity rather than a private lifestyle luxury. Societies investing in '
                      'sleep-friendly policies may harvest compound benefits across classrooms, '
                      'hospitals, and safety-critical workplaces. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes.'},
  'tfng': [{'question': 'Slow-wave sleep is linked to declarative memory stabilization.',
            'answer': 'True'},
           {'question': 'All sleep apps are validated by polysomnography studies.',
            'answer': 'False'},
           {'question': 'Every university has adopted later exam schedules.',
            'answer': 'Not Given'},
           {'question': 'Treating sleep apnoea may improve delayed recall.', 'answer': 'True'},
           {'question': 'Blue-light filters always eliminate pre-bed arousal effects.',
            'answer': 'False'}],
  'ynng': [{'question': 'The author rejects blaming individuals for structural sleep barriers.',
            'answer': 'Yes'},
           {'question': 'The writer believes sleep is merely a passive storage period.',
            'answer': 'No'},
           {'question': 'The author supports aligning school schedules with circadian science.',
            'answer': 'Yes'},
           {'question': 'The writer claims fatigue always invalidates eyewitness testimony.',
            'answer': 'No'},
           {'question': 'The author views sleep as a public good intersecting equity.',
            'answer': 'Yes'}],
  'matching_headings': [{'paragraph': 'B',
                         'correct': 'ii. Synaptic theories and causal replay tools'},
                        {'paragraph': 'C',
                         'correct': 'iii. Clinical disorders and public health limits'},
                        {'paragraph': 'D',
                         'correct': 'iv. School timing experiments and employer pilots'},
                        {'paragraph': 'E',
                         'correct': 'v. Technology, trackers, and orthosomnia risks'},
                        {'paragraph': 'F',
                         'correct': 'vi. Forensic testimony and interrogation policy'}],
  'headings_pool': ['i. Glacier tourism permit fees',
                    'j. Synaptic theories and causal replay tools',
                    'k. Clinical disorders and public health limits',
                    'l. School timing experiments and employer pilots',
                    'm. Technology, trackers, and orthosomnia risks',
                    'n. Forensic testimony and interrogation policy',
                    'o. Copper coin minting history'],
  'matching_info': [{'question': 'mention of optogenetics triggering replay', 'paragraph': 'B'},
                    {'question': 'reference to positive airway pressure treatment',
                     'paragraph': 'C'},
                    {'question': 'examples of delayed school start experiments', 'paragraph': 'D'},
                    {'question': 'discussion of orthosomnia from wearables', 'paragraph': 'E'},
                    {'question': 'a vision of personalised chronotype recommendations',
                     'paragraph': 'G'}],
  'sentence_completion': [{'question': 'Hippocampal and neocortical networks replay daytime ____.',
                           'answer': 'experiences'},
                          {'question': 'Synaptic homeostasis may downscale net synaptic ____.',
                           'answer': 'strength'},
                          {'question': 'Chronic short sleep links to biomarkers of ____.',
                           'answer': 'neurodegeneration'},
                          {'question': 'Adaptive software could pace review using sleep ____.',
                           'answer': 'architecture'}],
  'summary_completion': [{'question': 'REM sleep associates with emotional and ____ learning.',
                          'answer': 'procedural'},
                         {'question': 'Housing noise limits individual sleep hygiene ____.',
                          'answer': 'control'},
                         {'question': 'Judges apply expert testimony admissibility ____ unevenly.',
                          'answer': 'standards'},
                         {'question': 'Ethical safeguards should prevent penalising night ____.',
                          'answer': 'owls'}],
  'table_completion': [{'question': 'Education issue | Early bells may truncate adolescent sleep '
                                    '____',
                        'answer': 'opportunity'},
                       {'question': 'Technology | Content arousal can outweigh blue-light ____',
                        'answer': 'filters'},
                       {'question': 'Justice reform | Policies may cap consecutive interrogation '
                                    '____',
                        'answer': 'hours'}],
  'mcq': [{'question': 'Paragraph A indicates policymakers question',
           'options': ['lunar phases in exams',
                       'school start times for adolescents',
                       'eliminating all declarative memory',
                       'banning neuroimaging'],
           'answer': 'school start times for adolescents'},
          {'question': 'According to paragraph B, commercial sleep apps are problematic because',
           'options': ['science shows active selection not passive storage',
                       'slow waves do not exist',
                       'GABA is illegal',
                       'animals cannot learn'],
           'answer': 'science shows active selection not passive storage'},
          {'question': 'Paragraph D suggests later school bells require',
           'options': ['no transport changes',
                       'adjusting transport logistics',
                       'shorter curricula only',
                       'banning sports'],
           'answer': 'adjusting transport logistics'},
          {'question': 'Paragraph F warns against',
           'options': ['any sleep expert testimony',
                       'deterministic claims that fatigue always invalidates testimony',
                       'human rights protections',
                       'limits on interrogation'],
           'answer': 'deterministic claims that fatigue always invalidates testimony'},
          {'question': 'The final paragraph treats sleep as intersecting',
           'options': ['only luxury hospitality',
                       'cognition, health, and equity',
                       'marketing alone',
                       'coin collecting'],
           'answer': 'cognition, health, and equity'}],
  'short_answer': [{'question': 'Which sleep stage is tied to declarative memories?',
                    'answer': 'slow-wave',
                    'word_limit': 2},
                   {'question': 'What breathing treatment may improve recall in apnoea patients?',
                    'answer': 'airway pressure',
                    'word_limit': 2},
                   {'question': 'What term describes anxiety about imperfect sleep tracker data?',
                    'answer': 'orthosomnia',
                    'word_limit': 1},
                   {'question': 'What markers may accumulate faster with chronic short sleep?',
                    'answer': 'biomarkers',
                    'word_limit': 1}]},
 {'quiz_number': 10,
  'title': 'Extremophiles and astrobiology',
  'topic_category': 'Science',
  'paragraphs': {'A': 'Extremophiles thrive in environments once considered sterile, including '
                      'hyperacidic hot springs, deep subsurface brines, and polar deserts with '
                      'intense ultraviolet radiation. Their enzymes, membranes, and repair '
                      "pathways inform models of life's resilience on early Earth and potentially "
                      'on other planetary bodies. Astrobiologists use Antarctic dry valleys as '
                      'analogues for Martian soils, studying cryptoendolithic communities '
                      'sheltering inside translucent rocks. Space agencies isolate spacecraft '
                      'components to reduce forward contamination before missions search for '
                      'indigenous extraterrestrial biosignatures. Discoveries of subsurface oceans '
                      'on icy moons redirect sampling priorities toward plumes that might carry '
                      'organic material. Cross-disciplinary collaboration, sustained funding, and '
                      'careful communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'B': 'Thermophilic proteins maintain structural stability through additional '
                      'ionic bridges and compact hydrophobic cores resisting thermal unfolding. '
                      'Industry deploys heat-stable polymerases and cellulases in biofuel '
                      'pretreatment, translating evolutionary adaptations into commercial '
                      'biocatalysts. Laboratory directed evolution accelerates improvements but '
                      'risks overlooking context-dependent fitness trade-offs observed in natural '
                      'habitats. The author cautions that enzymes optimal in reactors may '
                      'underperform in complex environmental matrices containing inhibitors. '
                      'Bioprospecting agreements with indigenous communities near hot springs '
                      'remain ethically contested when benefit sharing is vague. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes. Cross-disciplinary collaboration, sustained funding, '
                      'and careful communication with affected communities remain central to '
                      'credible long-term outcomes.',
                 'C': 'Halophiles accumulate compatible solutes or pump ions to balance osmotic '
                      'stress in salt flats exceeding seawater salinity several fold. Pigments '
                      'such as bacteriorhodopsin enable energy capture where photosynthesis is '
                      'limited, inspiring research into optogenetic tools. Ancient evaporite '
                      'deposits may entomb dormant cells, raising methodological cautions when '
                      'interpreting DNA traces as active communities. Planetary protection '
                      'officers worry that terrestrial halophiles could survive on spacecraft '
                      'surfaces during multi-year transits. The writer supports stringent cleaning '
                      'protocols while noting that natural meteorite exchange historically mixed '
                      'rocky material between worlds. Cross-disciplinary collaboration, sustained '
                      'funding, and careful communication with affected communities remain central '
                      'to credible long-term outcomes.',
                 'D': 'Alkaliphiles maintain internal pH near neutrality while exporting protons '
                      'across membranes bathing in carbonate-rich lakes. Their novel pathways for '
                      'sulfur and nitrogen cycling expand metabolic maps used to design life '
                      'detection instrument target lists. Deep drilling projects in South African '
                      'gold mines revealed chemolithoautotrophs sustained by radiolytic water '
                      'splitting products. Such findings extend habitable volume estimates below '
                      'continents, relevant when imagining subsurface refugia on Mars. The author '
                      'argues subsurface biospheres deserve equal billing with surface '
                      'habitability in mission planning debates. Cross-disciplinary collaboration, '
                      'sustained funding, and careful communication with affected communities '
                      'remain central to credible long-term outcomes.',
                 'E': 'Radioresistant microbes repair double-strand breaks using multiple '
                      'redundant mechanisms studied for biotechnology and medicine. Simulated '
                      'microgravity experiments aboard stations examine whether extreme stress '
                      'responses alter biofilm formation on life support hardware. Closed-loop '
                      'habitat designers monitor microbial corrosion that could compromise water '
                      'recycling aboard long-duration crewed missions. Ethicists question whether '
                      'terraforming discussions should consider extremophile introductions even if '
                      'human survival appears dependent. The writer believes precautionary '
                      'frameworks must distinguish scientific sampling from irreversible ecosystem '
                      'seeding. Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes. Policymakers increasingly demand reproducible evidence, '
                      'open data, and independent evaluation before scaling interventions beyond '
                      'controlled pilot settings.',
                 'F': 'Public excitement about alien life sometimes oversimplifies ambiguous '
                      'biosignatures such as methane seasonal cycles on Mars. Spectroscopic '
                      'detections require ruling out abiotic geochemistry and atmospheric '
                      'transport before claiming biological production. Citizen science projects '
                      'classify morphology in microscope images, though expert validation remains '
                      'necessary to avoid false positives. Educators use extremophile stories to '
                      'teach evolutionary principles, linking astrobiology to classroom '
                      'biodiversity units. The author contends inspiring narratives should still '
                      'emphasise evidentiary standards that distinguish speculation from '
                      'discovery. Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes. Policymakers increasingly demand reproducible evidence, '
                      'open data, and independent evaluation before scaling interventions beyond '
                      'controlled pilot settings.',
                 'G': 'Future missions may combine drill cores with in situ sequencing chips '
                      'adapted from extremophile-compatible reagents. International treaties will '
                      'need updating if sample return protocols risk releasing novel organisms '
                      "into Earth's biosphere. The writer foresees interdisciplinary institutes "
                      'merging geology, microbiology, and instrumentation engineering under shared '
                      'funding. Such collaboration could accelerate responsible exploration while '
                      'nurturing terrestrial applications in medicine and green chemistry. '
                      'Extremophiles thus bridge planetary curiosity with practical innovation '
                      'when research ethics and environmental stewardship remain central. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes. Policymakers increasingly demand reproducible evidence, '
                      'open data, and independent evaluation before scaling interventions beyond '
                      'controlled pilot settings.'},
  'tfng': [{'question': 'Antarctic dry valleys serve as Mars analogues.', 'answer': 'True'},
           {'question': 'Every halophile depends on photosynthesis for energy.', 'answer': 'False'},
           {'question': "The passage confirms life exists in Europa's ocean today.",
            'answer': 'Not Given'},
           {'question': 'Radioresistant microbes have redundant DNA repair mechanisms.',
            'answer': 'True'},
           {'question': 'Spacecraft are never cleaned before launch.', 'answer': 'False'}],
  'ynng': [{'question': 'The author warns bioprospecting agreements need clear benefit sharing.',
            'answer': 'Yes'},
           {'question': 'The writer dismisses subsurface habitats as irrelevant to Mars.',
            'answer': 'No'},
           {'question': 'The author distinguishes sampling from irreversible ecosystem seeding.',
            'answer': 'Yes'},
           {'question': 'The writer believes ambiguous biosignatures should be announced as '
                        'confirmed life.',
            'answer': 'No'},
           {'question': 'The author values evidentiary standards in public education.',
            'answer': 'Yes'}],
  'matching_headings': [{'paragraph': 'B',
                         'correct': 'ii. Thermophile biochemistry and bioprospecting ethics'},
                        {'paragraph': 'C',
                         'correct': 'iii. Halophiles, pigments, and planetary protection'},
                        {'paragraph': 'D',
                         'correct': 'iv. Alkaliphiles and deep subsurface autotrophs'},
                        {'paragraph': 'E',
                         'correct': 'v. Radiation repair and habitat hardware risks'},
                        {'paragraph': 'F',
                         'correct': 'vi. Biosignatures, citizen science, and education'}],
  'headings_pool': ['i. Renaissance tapestry dye trade',
                    'j. Thermophile biochemistry and bioprospecting ethics',
                    'k. Halophiles, pigments, and planetary protection',
                    'l. Alkaliphiles and deep subsurface autotrophs',
                    'm. Radiation repair and habitat hardware risks',
                    'n. Biosignatures, citizen science, and education',
                    'o. Medieval cathedral acoustics'],
  'matching_info': [{'question': 'discussion of heat-stable enzymes in biofuel pretreatment',
                     'paragraph': 'B'},
                    {'question': 'reference to bacteriorhodopsin in salt flats', 'paragraph': 'C'},
                    {'question': 'mention of radiolytic water splitting in mines',
                     'paragraph': 'D'},
                    {'question': 'examples of microbial corrosion on life support',
                     'paragraph': 'E'},
                    {'question': 'vision of in situ sequencing on future missions',
                     'paragraph': 'G'}],
  'sentence_completion': [{'question': 'Cryptoendolithic communities shelter inside translucent '
                                       '____.',
                           'answer': 'rocks'},
                          {'question': 'Halophiles may accumulate compatible ____ to balance '
                                       'osmosis.',
                           'answer': 'solutes'},
                          {'question': 'Alkaliphiles export protons across ____.',
                           'answer': 'membranes'},
                          {'question': 'Sample return may require updated international ____.',
                           'answer': 'treaties'}],
  'summary_completion': [{'question': 'Space agencies reduce forward contamination before '
                                      'searching for ____.',
                          'answer': 'biosignatures'},
                         {'question': 'Directed evolution may miss context-dependent fitness ____.',
                          'answer': 'trade-offs'},
                         {'question': 'Methane seasonal cycles require ruling out abiotic ____.',
                          'answer': 'geochemistry'},
                         {'question': 'Interdisciplinary institutes may merge geology and ____.',
                          'answer': 'microbiology'}],
  'table_completion': [{'question': 'Mars analogue | Dry valleys host cryptoendolithic ____',
                        'answer': 'communities'},
                       {'question': 'Industry use | Thermophilic polymerases support ____ '
                                    'pretreatment',
                        'answer': 'biofuel'},
                       {'question': 'Ethics | Terraforming debates question extremophile ____',
                        'answer': 'introductions'}],
  'mcq': [{'question': 'Paragraph A indicates icy moons redirect priorities toward',
           'options': ['solar panel design',
                       'plumes that might carry organics',
                       'cathedral acoustics',
                       'tapestry dyes'],
           'answer': 'plumes that might carry organics'},
          {'question': 'According to paragraph B, bioprospecting near hot springs is contested due '
                       'to',
           'options': ['lack of any enzymes',
                       'vague benefit sharing',
                       'ban on evolution',
                       'absence of industry'],
           'answer': 'vague benefit sharing'},
          {'question': 'Paragraph D describes chemolithoautotrophs sustained by',
           'options': ['tourist donations',
                       'radiolytic water splitting products',
                       'only surface photosynthesis',
                       'spacecraft paint'],
           'answer': 'radiolytic water splitting products'},
          {'question': 'Paragraph F suggests citizen science requires',
           'options': ['no expert validation',
                       'expert validation to avoid false positives',
                       'abandoning spectroscopy',
                       'ignoring methane'],
           'answer': 'expert validation to avoid false positives'},
          {'question': 'The final paragraph links extremophiles to',
           'options': ['only science fiction',
                       'medicine and green chemistry applications',
                       'banning all drilling',
                       'ending planetary treaties'],
           'answer': 'medicine and green chemistry applications'}],
  'short_answer': [{'question': 'What valleys are used as Martian soil analogues?',
                    'answer': 'dry valleys',
                    'word_limit': 2},
                   {'question': 'What pigment enables energy capture for some halophiles?',
                    'answer': 'bacteriorhodopsin',
                    'word_limit': 1},
                   {'question': 'What stress do radioresistant microbes withstand?',
                    'answer': 'radiation',
                    'word_limit': 1},
                   {'question': 'What gas seasonal cycles are mentioned as ambiguous '
                                'biosignatures?',
                    'answer': 'methane',
                    'word_limit': 1}]},
 {'quiz_number': 11,
  'title': 'Artificial intelligence ethics',
  'topic_category': 'Technology',
  'paragraphs': {'A': 'Artificial intelligence systems increasingly influence hiring, lending, '
                      'policing, and medical triage, raising questions about fairness, '
                      'accountability, and transparency. Machine learning models trained on '
                      'historical data may reproduce discriminatory patterns unless developers '
                      'audit features and outcomes across demographic groups. Regulators propose '
                      'risk-based frameworks requiring documentation, human oversight, and '
                      'incident reporting for high-impact applications. Industry guidelines '
                      'emphasise privacy-preserving techniques, yet commercial incentives to '
                      'maximise predictive accuracy can conflict with interpretability goals. '
                      'Public consultations reveal uneven literacy about statistical uncertainty, '
                      'complicating democratic deliberation on acceptable error rates. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'B': 'Explainability research seeks post-hoc rationales for neural network '
                      'decisions through attention maps or surrogate models approximating complex '
                      'boundaries. Critics argue explanations may comfort users without revealing '
                      'causal mechanisms, creating illusions of understanding termed explanation '
                      'theater. Hybrid workflows keep humans reviewing edge cases, although '
                      'automation bias may cause reviewers to defer excessively to confident '
                      'algorithmic recommendations. The author insists that meaningful oversight '
                      'requires access to training data lineage and deployment context, not merely '
                      'polished user interfaces. Without institutional capacity to evaluate '
                      'claims, procurement officers may purchase opaque systems marketed as '
                      'revolutionary black boxes. Cross-disciplinary collaboration, sustained '
                      'funding, and careful communication with affected communities remain central '
                      'to credible long-term outcomes.',
                 'C': 'Facial recognition deployments sparked moratoria in cities concerned about '
                      'misidentification disproportionately harming darker-skinned individuals. '
                      'Independent benchmarks demonstrated higher false match rates under poor '
                      'lighting, prompting lawsuits and legislative bans in public spaces. '
                      'Security agencies counter that controlled gallery searches assist '
                      'investigations, advocating narrow warrants and audit logs. Civil society '
                      'groups demand sunset clauses forcing periodic reassessment as accuracy '
                      'improves or surveillance normalises. The writer believes democratic '
                      'societies must choose whether convenience security trade-offs align with '
                      'constitutional protections. Cross-disciplinary collaboration, sustained '
                      'funding, and careful communication with affected communities remain central '
                      'to credible long-term outcomes. Policymakers increasingly demand '
                      'reproducible evidence, open data, and independent evaluation before scaling '
                      'interventions beyond controlled pilot settings.',
                 'D': 'Generative models capable of synthesising text, images, and audio introduce '
                      'copyright, consent, and misinformation challenges at scale. Creators seek '
                      'compensation when training corpora include proprietary works scraped '
                      'without licences. Watermarking and provenance standards attempt to label '
                      'synthetic media, though adversaries can often remove fragile markers. '
                      'Educational institutions revise assessment policies as students submit '
                      'machine-generated essays difficult to distinguish from original prose. The '
                      'author contends that literacy programmes should teach verification habits '
                      'rather than relying solely on detection arms races. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes.',
                 'E': 'Autonomous weapons debates illustrate extreme cases where delegated lethal '
                      'decisions lack meaningful human judgment in compressed timelines. '
                      'Diplomatic talks pursue voluntary commitments, while activists campaign for '
                      'binding treaties mirroring chemical weapons prohibitions. Military planners '
                      'highlight swarming drones overwhelming defences, complicating simplistic '
                      'bans without verification mechanisms. Ethicists stress that dual-use '
                      'components blur lines between civilian logistics robots and militarised '
                      'platforms. The writer urges international forums to prioritise inspectable '
                      'constraints over vague principles ignored after procurement cycles. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes. Policymakers increasingly demand reproducible evidence, '
                      'open data, and independent evaluation before scaling interventions beyond '
                      'controlled pilot settings.',
                 'F': 'Corporate environmental claims about AI efficiency sometimes ignore rising '
                      'energy use from ever-larger model training runs. Researchers publish carbon '
                      'footprints comparing cloud regions powered by renewables versus '
                      'fossil-heavy grids. Hardware accelerators improve inference efficiency, yet '
                      'rebound effects may increase total deployments offsetting gains. Policy '
                      'proposals mandate disclosure of energy consumption for public sector AI '
                      'contracts above threshold budgets. The author argues sustainability metrics '
                      'belong alongside accuracy benchmarks in responsible innovation scorecards. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes. Policymakers increasingly demand reproducible evidence, '
                      'open data, and independent evaluation before scaling interventions beyond '
                      'controlled pilot settings.',
                 'G': 'Looking ahead, interdisciplinary ethics boards integrating law, sociology, '
                      'and engineering may guide product roadmaps before harm becomes entrenched. '
                      'Whistleblower protections could encourage employees to report reckless '
                      'deployments without career retaliation. Open model cards describing '
                      'limitations may reduce misuse if paired with enforceable terms of service. '
                      'The writer maintains technology is neither inherently ethical nor '
                      'unethical; governance choices determine societal outcomes. Investing in '
                      'civic expertise now may prevent brittle reactive bans that stifle '
                      'beneficial applications along with harmful ones. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.'},
  'tfng': [{'question': 'Historical training data can embed discriminatory patterns.',
            'answer': 'True'},
           {'question': 'Every city has permanently banned all facial recognition.',
            'answer': 'Not Given'},
           {'question': 'Explainability methods always reveal true causal mechanisms.',
            'answer': 'False'},
           {'question': 'Generative models raise copyright and misinformation issues.',
            'answer': 'True'},
           {'question': 'The passage states all militaries abandoned autonomous weapons research.',
            'answer': 'Not Given'}],
  'ynng': [{'question': 'The author wants oversight based on data lineage not only polished '
                        'interfaces.',
            'answer': 'Yes'},
           {'question': 'The writer believes explanation theater provides sufficient '
                        'accountability.',
            'answer': 'No'},
           {'question': 'The author supports verification literacy over sole reliance on '
                        'detectors.',
            'answer': 'Yes'},
           {'question': 'The writer claims larger models always reduce total energy use.',
            'answer': 'No'},
           {'question': 'The author sees governance choices as determining AI outcomes.',
            'answer': 'Yes'}],
  'matching_headings': [{'paragraph': 'B',
                         'correct': 'ii. Explainability limits and automation bias'},
                        {'paragraph': 'C',
                         'correct': 'iii. Facial recognition moratoria and audits'},
                        {'paragraph': 'D', 'correct': 'iv. Generative media and assessment policy'},
                        {'paragraph': 'E', 'correct': 'v. Autonomous weapons diplomacy'},
                        {'paragraph': 'F',
                         'correct': 'vi. Energy footprints and disclosure rules'}],
  'headings_pool': ['i. Baroque opera costume inventories',
                    'j. Explainability limits and automation bias',
                    'k. Facial recognition moratoria and audits',
                    'l. Generative media and assessment policy',
                    'm. Autonomous weapons diplomacy',
                    'n. Energy footprints and disclosure rules',
                    'o. Silk road caravan taxation'],
  'matching_info': [{'question': 'discussion of automation bias among human reviewers',
                     'paragraph': 'B'},
                    {'question': 'reference to false match rates under poor lighting',
                     'paragraph': 'C'},
                    {'question': 'mention of watermarking synthetic media', 'paragraph': 'D'},
                    {'question': 'examples of swarming drone concerns', 'paragraph': 'E'},
                    {'question': 'vision of interdisciplinary ethics boards', 'paragraph': 'G'}],
  'sentence_completion': [{'question': 'Risk-based frameworks may require human ____ for '
                                       'high-impact AI.',
                           'answer': 'oversight'},
                          {'question': 'Surrogate models approximate complex decision ____.',
                           'answer': 'boundaries'},
                          {'question': 'Creators seek compensation when corpora lack ____.',
                           'answer': 'licences'},
                          {'question': 'Model cards describe limitations when paired with '
                                       'enforceable ____.',
                           'answer': 'terms'}],
  'summary_completion': [{'question': 'Audits should examine outcomes across demographic ____.',
                          'answer': 'groups'},
                         {'question': 'Civil society groups demand sunset ____ for reassessment.',
                          'answer': 'clauses'},
                         {'question': 'Hardware accelerators may face rebound ____ increasing '
                                      'deployments.',
                          'answer': 'effects'},
                         {'question': 'Whistleblower protections could reduce career ____.',
                          'answer': 'retaliation'}],
  'table_completion': [{'question': 'Fairness tool | Feature audits address historical ____',
                        'answer': 'bias'},
                       {'question': 'Security debate | Narrow warrants may accompany gallery ____',
                        'answer': 'searches'},
                       {'question': 'Sustainability | Training runs consume cloud ____',
                        'answer': 'energy'}],
  'mcq': [{'question': 'Paragraph A indicates regulators focus on',
           'options': ['banning all statistics',
                       'documentation and incident reporting',
                       'eliminating human review always',
                       'ignoring privacy'],
           'answer': 'documentation and incident reporting'},
          {'question': 'According to paragraph B, procurement risk arises when',
           'options': ['officers can evaluate all data lineage',
                       'systems are sold as opaque black boxes',
                       'neural networks are illegal',
                       'attention maps are mandatory'],
           'answer': 'systems are sold as opaque black boxes'},
          {'question': 'Paragraph D suggests schools should teach',
           'options': ['only watermark removal',
                       'verification habits for synthetic content',
                       'banning essays entirely',
                       'scraping without licences'],
           'answer': 'verification habits for synthetic content'},
          {'question': 'Paragraph F notes rebound effects may',
           'options': ['reduce all deployments',
                       'increase total deployments offsetting efficiency',
                       'eliminate renewables',
                       'ban public contracts'],
           'answer': 'increase total deployments offsetting efficiency'},
          {'question': 'The final paragraph warns reactive bans may',
           'options': ['stifle beneficial and harmful applications alike',
                       'guarantee perfect ethics boards',
                       'remove need for whistleblowers',
                       'end engineering input'],
           'answer': 'stifle beneficial and harmful applications alike'}],
  'short_answer': [{'question': 'What bias may cause humans to defer to algorithms?',
                    'answer': 'automation',
                    'word_limit': 1},
                   {'question': 'What term describes comforting but shallow explanations?',
                    'answer': 'theater',
                    'word_limit': 1},
                   {'question': 'What lethal systems lack judgment in compressed timelines?',
                    'answer': 'weapons',
                    'word_limit': 1},
                   {'question': 'What documents may disclose energy use in public contracts?',
                    'answer': 'footprints',
                    'word_limit': 1}]},
 {'quiz_number': 12,
  'title': 'Blockchain beyond cryptocurrency',
  'topic_category': 'Technology',
  'paragraphs': {'A': 'Distributed ledger technologies record transactions across replicated nodes '
                      'using cryptographic hashing to detect tampering without a single central '
                      'authority. Beyond cryptocurrency speculation, enterprises explore supply '
                      'chain traceability, digital identity wallets, and programmable settlement '
                      'through smart contracts. Consensus mechanisms such as proof of stake reduce '
                      'energy intensity compared with early proof-of-work mining, though '
                      'scalability trade-offs persist. Regulators classify some tokens as '
                      'securities, commodities, or utility instruments, creating compliance '
                      'uncertainty for global platforms. Pilots must demonstrate advantages over '
                      'conventional databases before taxpayers fund large-scale public sector '
                      'deployments. Cross-disciplinary collaboration, sustained funding, and '
                      'careful communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'B': 'Permissioned blockchains limit validator membership to consortium '
                      'participants, trading openness for throughput suitable to interbank '
                      'reconciliation. Hyperledger and similar frameworks integrate role-based '
                      'access controls familiar to corporate information technology departments. '
                      'Critics note that immutability complicates error correction when fraudulent '
                      'entries slip past weak onboarding procedures. The author recommends pairing '
                      'ledgers with off-chain dispute resolution rather than treating code as '
                      'infallible law. Hybrid architectures anchor periodic state summaries on '
                      'public chains while storing detailed records privately. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes. Policymakers '
                      'increasingly demand reproducible evidence, open data, and independent '
                      'evaluation before scaling interventions beyond controlled pilot settings.',
                 'C': 'Smart contracts execute predefined logic when conditions trigger, '
                      'automating insurance payouts after parametric weather thresholds or flight '
                      'delays. Coding flaws have drained funds through reentrancy vulnerabilities, '
                      'prompting formal verification tools and audited libraries. Legal scholars '
                      'question whether self-executing scripts satisfy contract formation '
                      'requirements in every jurisdiction. Consumers need plain-language '
                      'disclosures explaining irreversible transfers when private keys are lost. '
                      'The writer believes developer education must include security culture '
                      'alongside entrepreneurial pitch competitions. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes. Policymakers '
                      'increasingly demand reproducible evidence, open data, and independent '
                      'evaluation before scaling interventions beyond controlled pilot settings.',
                 'D': 'Supply chain applications tag batches with unique identifiers scanned at '
                      'ports, warehouses, and retail shelves. Provenance claims for '
                      'pharmaceuticals and luxury goods deter counterfeiting if independent '
                      'auditors verify uploads. Smallholder farmers may lack connectivity to '
                      'participate equally, risking exclusion from premium traceability markets. '
                      'Standards bodies work on interoperable schemas so competing platforms do '
                      'not fragment data silos. The author contends social benefit requires '
                      'inclusive onboarding, not merely impressive pilot press releases. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes. Policymakers increasingly demand reproducible evidence, '
                      'open data, and independent evaluation before scaling interventions beyond '
                      'controlled pilot settings.',
                 'E': 'Digital identity wallets let holders present verifiable credentials without '
                      'revealing entire document images on each check. Governments pilot '
                      'decentralised identifiers for licences and tax filings, debating custody '
                      'models between citizens and state vaults. Privacy advocates warn that '
                      'immutable attendance logs could enable perpetual surveillance if '
                      'correlation becomes trivial. Revocation lists must update quickly when '
                      'credentials expire or investigations invalidate prior certifications. The '
                      'writer supports user-controlled disclosure minimisation principles embedded '
                      'in protocol design choices. Cross-disciplinary collaboration, sustained '
                      'funding, and careful communication with affected communities remain central '
                      'to credible long-term outcomes. Policymakers increasingly demand '
                      'reproducible evidence, open data, and independent evaluation before scaling '
                      'interventions beyond controlled pilot settings.',
                 'F': 'Environmental, social, and governance investors scrutinise blockchain '
                      'projects for greenwashing when marketing claims exceed measured impact. '
                      'Carbon accounting for node operations varies widely depending on regional '
                      'electricity mixes powering validators. Tokenised carbon credits face '
                      'double-counting risks if registries are not synchronised with national '
                      'inventories. Academic reviews urge transparent methodology before climate '
                      'finance flows toward unproven ledger gimmicks. The author argues '
                      'measurement discipline protects legitimate use cases from reputational '
                      'contagion of speculative excess. Cross-disciplinary collaboration, '
                      'sustained funding, and careful communication with affected communities '
                      'remain central to credible long-term outcomes. Policymakers increasingly '
                      'demand reproducible evidence, open data, and independent evaluation before '
                      'scaling interventions beyond controlled pilot settings.',
                 'G': 'Interoperability bridges linking heterogeneous chains introduce attack '
                      'surfaces exploited in high-profile thefts. Insurance and custody services '
                      'mature slowly, leaving retail participants exposed to exchange failures. '
                      'Central bank digital currencies may coexist with enterprise ledgers, each '
                      'optimising different policy goals. The writer foresees consolidation around '
                      'protocols demonstrating security, compliance, and measurable efficiency '
                      'gains. Blockchain will remain a niche tool unless advocates honestly '
                      'address limits rather than promising universal disruption. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes. Policymakers increasingly demand reproducible evidence, '
                      'open data, and independent evaluation before scaling interventions beyond '
                      'controlled pilot settings.'},
  'tfng': [{'question': 'Proof of stake generally uses less energy than early proof-of-work '
                        'mining.',
            'answer': 'True'},
           {'question': 'Smart contracts have never suffered security vulnerabilities.',
            'answer': 'False'},
           {'question': 'Every government has launched a digital identity wallet.',
            'answer': 'Not Given'},
           {'question': 'Permissioned blockchains restrict who may validate transactions.',
            'answer': 'True'},
           {'question': 'The passage claims blockchain always outperforms all conventional '
                        'databases.',
            'answer': 'False'}],
  'ynng': [{'question': 'The author recommends off-chain dispute resolution alongside ledgers.',
            'answer': 'Yes'},
           {'question': 'The writer believes lost private keys are easily reversible on chain.',
            'answer': 'No'},
           {'question': 'The author stresses inclusive farmer onboarding for supply chains.',
            'answer': 'Yes'},
           {'question': 'The writer thinks marketing alone proves environmental impact.',
            'answer': 'No'},
           {'question': 'The author expects honest discussion of limits for adoption.',
            'answer': 'Yes'}],
  'matching_headings': [{'paragraph': 'B',
                         'correct': 'ii. Consortium validators and hybrid anchoring'},
                        {'paragraph': 'C', 'correct': 'iii. Smart contract risks and legal status'},
                        {'paragraph': 'D',
                         'correct': 'iv. Traceability standards and farmer access'},
                        {'paragraph': 'E', 'correct': 'v. Verifiable credentials and revocation'},
                        {'paragraph': 'F', 'correct': 'vi. ESG scrutiny and carbon token risks'}],
  'headings_pool': ['i. Medieval guild apprenticeship fees',
                    'j. Consortium validators and hybrid anchoring',
                    'k. Smart contract risks and legal status',
                    'l. Traceability standards and farmer access',
                    'm. Verifiable credentials and revocation',
                    'n. ESG scrutiny and carbon token risks',
                    'o. Victorian railway dining menus'],
  'matching_info': [{'question': 'mention of periodic state summaries on public chains',
                     'paragraph': 'B'},
                    {'question': 'reference to reentrancy vulnerabilities', 'paragraph': 'C'},
                    {'question': 'discussion of interoperable schemas for supply chains',
                     'paragraph': 'D'},
                    {'question': 'examples of decentralised identifiers for licences',
                     'paragraph': 'E'},
                    {'question': 'a conclusion about consolidation around secure protocols',
                     'paragraph': 'G'}],
  'sentence_completion': [{'question': 'Cryptographic hashing helps detect ____ without central '
                                       'authority.',
                           'answer': 'tampering'},
                          {'question': 'Parametric insurance may pay after weather ____.',
                           'answer': 'thresholds'},
                          {'question': 'Verifiable credentials avoid revealing full document ____.',
                           'answer': 'images'},
                          {'question': 'Bridges between chains can enlarge attack ____.',
                           'answer': 'surfaces'}],
  'summary_completion': [{'question': 'Regulators may classify tokens as securities or ____.',
                          'answer': 'commodities'},
                         {'question': 'Formal verification tools respond to coding ____.',
                          'answer': 'flaws'},
                         {'question': 'Revocation lists must update when credentials ____.',
                          'answer': 'expire'},
                         {'question': 'Central bank digital currencies may coexist with enterprise '
                                      '____.',
                          'answer': 'ledgers'}],
  'table_completion': [{'question': 'Consensus | Proof of stake lowers energy ____',
                        'answer': 'intensity'},
                       {'question': 'Supply chain | Auditors must verify uploaded ____',
                        'answer': 'provenance'},
                       {'question': 'Climate finance | Tokenised credits risk double ____',
                        'answer': 'counting'}],
  'mcq': [{'question': 'Paragraph A says enterprises explore blockchains for',
           'options': ['only cryptocurrency trading',
                       'traceability and digital identity among other uses',
                       'banning all smart contracts',
                       'replacing every database instantly'],
           'answer': 'traceability and digital identity among other uses'},
          {'question': 'According to paragraph B, immutability can complicate',
           'options': ['error correction after fraudulent entries',
                       'increasing validator openness always',
                       'eliminating access controls',
                       'banning hybrid architectures'],
           'answer': 'error correction after fraudulent entries'},
          {'question': 'Paragraph D indicates smallholders may lack',
           'options': ['luxury goods entirely',
                       'connectivity to join traceability markets',
                       'any agricultural output',
                       'port scanners'],
           'answer': 'connectivity to join traceability markets'},
          {'question': 'Paragraph F warns tokenised carbon credits may face',
           'options': ['automatic national synchronisation',
                       'double-counting without registry links',
                       'no investor interest',
                       'proof-of-work mandates'],
           'answer': 'double-counting without registry links'},
          {'question': 'The final paragraph predicts niche status unless advocates',
           'options': ['promise universal disruption',
                       'address limits honestly',
                       'ban custody services',
                       'ignore compliance'],
           'answer': 'address limits honestly'}],
  'short_answer': [{'question': 'What mechanism reduced energy use versus early mining?',
                    'answer': 'proof of stake',
                    'word_limit': 3},
                   {'question': 'What vulnerability type drained funds from flawed contracts?',
                    'answer': 'reentrancy',
                    'word_limit': 1},
                   {'question': 'What investors scrutinise projects for greenwashing?',
                    'answer': 'ESG',
                    'word_limit': 1},
                   {'question': 'What policy instruments may coexist with enterprise ledgers?',
                    'answer': 'digital currencies',
                    'word_limit': 2}]},
 {'quiz_number': 13,
  'title': 'Fifth-generation mobile networks',
  'topic_category': 'Technology',
  'paragraphs': {'A': 'Fifth-generation mobile networks promise higher throughput, lower latency, '
                      'and massive machine-type connectivity supporting industrial automation and '
                      'telemedicine. Radio access networks combine mid-band spectrum with dense '
                      'small cells, while core architectures virtualise functions in cloud data '
                      'centres. Network slicing allocates isolated logical networks on shared '
                      'hardware, enabling customised quality of service for emergency services '
                      'versus consumer streaming. Deployment costs drive co-investment models '
                      'between operators and municipalities seeking smart city applications on '
                      'lamp posts. Regulators auction spectrum bands with coverage obligations to '
                      'reduce rural digital divides that earlier generations widened. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'B': 'Millimetre-wave frequencies offer wide bandwidth yet suffer penetration '
                      'losses, requiring line-of-sight planning in urban canyons. Beamforming '
                      'arrays steer energy toward user equipment, improving spectral efficiency '
                      'while complicating interference management between neighbours. Drive tests '
                      'map received signal strength, guiding technicians adjusting tilt and power '
                      'to minimise dead zones in stadiums. The author notes marketing peak speeds '
                      'rarely match everyday experience when users share congested cells during '
                      'events. Realistic benchmarks should report median performance under loaded '
                      'conditions, not laboratory peak demonstrations alone. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes.',
                 'C': 'Edge computing places computation near base stations to support autonomous '
                      'vehicle coordination and augmented reality overlays with tight latency '
                      'budgets. Content delivery networks cache popular video closer to '
                      'subscribers, reducing backhaul strain on fibre links. Security architects '
                      'segment slices to prevent compromised internet-of-things devices from '
                      'pivoting into corporate virtual private networks. Zero-touch provisioning '
                      'automates onboarding thousands of sensors, though misconfigured '
                      'certificates can open widespread vulnerabilities. The writer urges '
                      'security-by-design reviews before citywide sensor rollouts marketed as '
                      'innovation showcases. Cross-disciplinary collaboration, sustained funding, '
                      'and careful communication with affected communities remain central to '
                      'credible long-term outcomes. Cross-disciplinary collaboration, sustained '
                      'funding, and careful communication with affected communities remain central '
                      'to credible long-term outcomes.',
                 'D': 'Telemedicine pilots transmit high-resolution imaging from ambulances using '
                      'guaranteed bitrate slices prioritised over recreational traffic. Rural '
                      'clinics connect to urban specialists, yet reimbursement rules and licensure '
                      'borders lag technical capability. Emergency drones relay situational video '
                      'to incident commanders when terrestrial links saturate during disasters. '
                      'Clinicians demand reliability metrics exceeding consumer service level '
                      'agreements before trusting remote surgical guidance. The author contends '
                      'healthcare adoption depends on institutional reform, not merely faster '
                      'radios. Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes. Policymakers increasingly demand reproducible evidence, '
                      'open data, and independent evaluation before scaling interventions beyond '
                      'controlled pilot settings.',
                 'E': 'Energy consumption of active antenna units raises sustainability questions '
                      'as traffic grows exponentially with video streaming. Sleep modes and '
                      'intelligent shutdown during low demand hours reduce power draw, requiring '
                      'coordination with always-on public safety slices. Operators purchase '
                      'renewable energy credits, while critics request direct power purchase '
                      'agreements tied to new wind farms. Lifecycle assessments include embodied '
                      'carbon in equipment manufacturing and difficult e-waste recycling for '
                      'complex radios. The writer believes transparent energy reporting should '
                      'accompany coverage maps in regulatory filings. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes.',
                 'F': 'Geopolitical tensions influence supplier diversification as governments '
                      'publish trusted vendor lists for critical infrastructure. Open radio access '
                      'network interfaces aim to reduce vendor lock-in by standardising '
                      'interoperability between radios and software stacks. Incumbent suppliers '
                      'argue open interfaces may fragment testing ecosystems, increasing '
                      'integration risk for smaller operators. Multilateral forums negotiate '
                      'mutual recognition of equipment certifications to avoid fragmented global '
                      'markets. The author supports competition if security assurance processes '
                      'keep pace with rapid interface experimentation. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes. Policymakers '
                      'increasingly demand reproducible evidence, open data, and independent '
                      'evaluation before scaling interventions beyond controlled pilot settings.',
                 'G': 'Sixth-generation research already explores terahertz communications and '
                      'integrated sensing, though standards remain years away. Backward '
                      'compatibility ensures legacy devices remain serviceable during lengthy '
                      'transition periods spanning a decade or more. The writer expects '
                      'fifth-generation investments to mature into dependable utilities when hype '
                      'yields to measured performance disclosure. Inclusive planning must connect '
                      'underserved households with affordable devices, not only install radios in '
                      'affluent districts. Ultimately, cellular evolution succeeds when policy, '
                      'engineering, and community needs align rather than chasing leaderboard '
                      'speeds. Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.'},
  'tfng': [{'question': 'Network slicing can provide customised quality of service.',
            'answer': 'True'},
           {'question': 'Millimetre-wave signals penetrate buildings easily without planning.',
            'answer': 'False'},
           {'question': 'Every country has completed rural 5G coverage.', 'answer': 'Not Given'},
           {'question': 'Edge computing can reduce latency for augmented reality.',
            'answer': 'True'},
           {'question': 'The passage states sixth-generation standards are already finalised '
                        'globally.',
            'answer': 'False'}],
  'ynng': [{'question': 'The author wants median loaded performance reported realistically.',
            'answer': 'Yes'},
           {'question': 'The writer believes faster radios alone fix healthcare reimbursement '
                        'barriers.',
            'answer': 'No'},
           {'question': 'The author supports transparent energy reporting with coverage maps.',
            'answer': 'Yes'},
           {'question': 'The writer claims open interfaces always eliminate integration risk.',
            'answer': 'No'},
           {'question': 'The author emphasises inclusive affordable device access.',
            'answer': 'Yes'}],
  'matching_headings': [{'paragraph': 'B', 'correct': 'ii. Beamforming and realistic speed claims'},
                        {'paragraph': 'C', 'correct': 'iii. Edge security and sensor onboarding'},
                        {'paragraph': 'D',
                         'correct': 'iv. Telemedicine slices and institutional barriers'},
                        {'paragraph': 'E', 'correct': 'v. Antenna energy and renewable sourcing'},
                        {'paragraph': 'F',
                         'correct': 'vi. Open interfaces and vendor diversification'}],
  'headings_pool': ['i. Renaissance fresco pigment trade',
                    'j. Beamforming and realistic speed claims',
                    'k. Edge security and sensor onboarding',
                    'l. Telemedicine slices and institutional barriers',
                    'm. Antenna energy and renewable sourcing',
                    'n. Open interfaces and vendor diversification',
                    'o. Ancient pottery kiln temperatures'],
  'matching_info': [{'question': 'discussion of beam steering toward user equipment',
                     'paragraph': 'B'},
                    {'question': 'reference to zero-touch provisioning risks', 'paragraph': 'C'},
                    {'question': 'examples of ambulance imaging with guaranteed bitrate',
                     'paragraph': 'D'},
                    {'question': 'mention of sleep modes for antenna units', 'paragraph': 'E'},
                    {'question': 'a balanced conclusion about community needs and engineering',
                     'paragraph': 'G'}],
  'sentence_completion': [{'question': 'Virtualised core functions run in cloud data ____.',
                           'answer': 'centres'},
                          {'question': 'Beamforming improves spectral ____ in dense areas.',
                           'answer': 'efficiency'},
                          {'question': 'Misconfigured certificates can open widespread ____.',
                           'answer': 'vulnerabilities'},
                          {'question': 'Terahertz research belongs to prospective ____ generation '
                                       'work.',
                           'answer': 'sixth'}],
  'summary_completion': [{'question': 'Mid-band spectrum pairs with dense small ____.',
                          'answer': 'cells'},
                         {'question': 'Drive tests map received signal ____.',
                          'answer': 'strength'},
                         {'question': 'Open interfaces aim to reduce vendor lock-____.',
                          'answer': 'in'},
                         {'question': 'Backward compatibility supports lengthy transition ____.',
                          'answer': 'periods'}],
  'table_completion': [{'question': 'Urban challenge | Millimetre-wave needs line-of-sight ____',
                        'answer': 'planning'},
                       {'question': 'Healthcare | Clinicians want reliability beyond consumer ____',
                        'answer': 'agreements'},
                       {'question': 'Sustainability | Lifecycle includes embodied carbon in ____',
                        'answer': 'manufacturing'}],
  'mcq': [{'question': 'Paragraph A describes slicing as',
           'options': ['physical copper replacement',
                       'isolated logical networks on shared hardware',
                       'ban on emergency traffic',
                       'single consumer queue only'],
           'answer': 'isolated logical networks on shared hardware'},
          {'question': 'According to paragraph B, marketing peaks may mislead because',
           'options': ['users never share cells',
                       'congestion lowers everyday experience',
                       'beamforming is illegal',
                       'drive tests are impossible'],
           'answer': 'congestion lowers everyday experience'},
          {'question': 'Paragraph D suggests telemedicine adoption needs',
           'options': ['only faster download speeds',
                       'institutional reform beyond radios',
                       'eliminating specialists',
                       'banning drones'],
           'answer': 'institutional reform beyond radios'},
          {'question': 'Paragraph F indicates open RAN aims to',
           'options': ['increase lock-in',
                       'standardise interoperability',
                       'ban certifications',
                       'end competition'],
           'answer': 'standardise interoperability'},
          {'question': 'The final paragraph argues success requires',
           'options': ['chasing leaderboard speeds alone',
                       'aligning policy, engineering, and community needs',
                       'ignoring legacy devices',
                       'ending affordable devices'],
           'answer': 'aligning policy, engineering, and community needs'}],
  'short_answer': [{'question': 'What architecture virtualises core network functions?',
                    'answer': 'cloud',
                    'word_limit': 1},
                   {'question': 'What technique steers radio energy toward devices?',
                    'answer': 'beamforming',
                    'word_limit': 1},
                   {'question': 'What open network model reduces vendor lock-in?',
                    'answer': 'RAN',
                    'word_limit': 1},
                   {'question': 'What frequency band suffers penetration losses?',
                    'answer': 'millimetre-wave',
                    'word_limit': 1}]},
 {'quiz_number': 14,
  'title': 'Zero-trust cybersecurity',
  'topic_category': 'Technology',
  'paragraphs': {'A': 'Zero-trust security models assume network perimeters are insufficient '
                      'because compromised credentials and insider threats already operate inside '
                      'traditional castle-and-moat architectures. Policies enforce continuous '
                      'verification of user identity, device health, and contextual risk before '
                      'granting least-privilege access to applications. Micro-segmentation limits '
                      'lateral movement by isolating workloads behind software-defined boundaries '
                      'monitored for anomalous east-west traffic. Migration from legacy virtual '
                      'private networks requires inventorying shadow information technology assets '
                      'discovered only after breaches. Executives fund pilots when insurers link '
                      'premiums to demonstrated identity governance maturity. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes.',
                 'B': 'Identity providers integrate multifactor authentication with '
                      'phishing-resistant hardware keys and conditional access policies evaluating '
                      'geolocation anomalies. Single sign-on portals streamline user experience '
                      'yet become high-value targets requiring hardened monitoring and rapid '
                      'revocation workflows. Service accounts for automation inherit excessive '
                      'permissions unless just-in-time elevation grants temporary rights with '
                      'approval trails. The author warns that checkbox compliance audits may '
                      'certify processes while leaving exploitable misconfigurations untouched in '
                      'production. Red teams routinely demonstrate privilege escalation paths '
                      'overlooked when diagrams depict idealised future states. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes.',
                 'C': 'Endpoint detection agents collect telemetry on process lineage, registry '
                      'changes, and memory injections indicative of ransomware precursors. '
                      'Security operations centres correlate alerts using graph analytics linking '
                      'users, devices, and cloud resources across hybrid estates. Alert fatigue '
                      'causes analysts to dismiss true positives, prompting tuning guided by '
                      'threat intelligence on sector-specific tactics. Machine learning models '
                      'flag anomalies but require human validation to avoid disruptive false '
                      'lockouts during patch windows. The writer advocates measurable '
                      'mean-time-to-contain metrics rather than vanity counts of blocked malware '
                      'samples. Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'D': 'Cloud workload protection scans infrastructure-as-code templates before '
                      'deployment, rejecting publicly exposed storage buckets automatically. '
                      'DevSecOps pipelines embed secret scanning to prevent API keys leaking into '
                      'public repositories indexed within minutes. Container images undergo '
                      'vulnerability assessment at build time, though prioritisation must consider '
                      'exploitability in runtime contexts. Developers resist friction unless '
                      'security teams provide autofix suggestions integrated into familiar '
                      'integrated development environments. The author believes developer empathy '
                      'accelerates adoption more than punitive gatekeeping at release deadlines. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes. Policymakers increasingly demand reproducible evidence, '
                      'open data, and independent evaluation before scaling interventions beyond '
                      'controlled pilot settings.',
                 'E': 'Supply chain attacks compromise trusted software updates, compelling '
                      'software bill of materials transparency and cryptographic signing of '
                      'artefacts. Vendors undergo continuous monitoring rather than annual '
                      'questionnaire exercises that snapshot outdated controls. Small '
                      'municipalities struggle to afford managed detection services, widening gaps '
                      'between well-resourced and underfunded agencies. Federal grant programmes '
                      'attempt to subsidise baseline zero-trust tooling for schools and hospitals. '
                      'The writer contends equitable cyber resilience is public infrastructure, '
                      'not a luxury for Fortune-listed companies alone. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes. Policymakers '
                      'increasingly demand reproducible evidence, open data, and independent '
                      'evaluation before scaling interventions beyond controlled pilot settings.',
                 'F': 'Privacy regulations intersect zero-trust logging because extensive '
                      'telemetry may capture personal communications metadata. Data minimisation '
                      'and retention limits must balance forensic needs with legal obligations to '
                      'delete stale records. Employee representatives negotiate monitoring scope '
                      'in works councils, especially for remote home networks blurred with '
                      'personal use. Transparency reports explaining what is logged can reduce '
                      'suspicion compared with opaque surveillance narratives. The author supports '
                      'accountable monitoring frameworks audited by independent privacy officers. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes. Policymakers increasingly demand reproducible evidence, '
                      'open data, and independent evaluation before scaling interventions beyond '
                      'controlled pilot settings.',
                 'G': 'Maturing programmes integrate disaster recovery exercises simulating '
                      'identity provider outages that could lock entire organisations out. '
                      'Break-glass credentials require sealed procedures tested quarterly to '
                      'prevent abuse while ensuring continuity. The writer expects zero-trust to '
                      'become baseline hygiene akin to patching, not a marketing slogan discarded '
                      'after breaches fade. Cross-sector information sharing on indicators of '
                      'compromise strengthens collective defence without blaming victims publicly. '
                      'Sustained leadership attention determines whether architecture diagrams '
                      'translate into daily operational habits protecting citizens. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes. Policymakers increasingly demand reproducible evidence, '
                      'open data, and independent evaluation before scaling interventions beyond '
                      'controlled pilot settings.'},
  'tfng': [{'question': 'Zero-trust assumes insiders or compromised credentials may already be '
                        'inside.',
            'answer': 'True'},
           {'question': 'Annual vendor questionnaires alone provide continuous monitoring in the '
                        'described model.',
            'answer': 'False'},
           {'question': 'Every municipality funds managed detection without grants.',
            'answer': 'Not Given'},
           {'question': 'Software bills of materials aim to improve supply chain transparency.',
            'answer': 'True'},
           {'question': 'Machine learning alerts never require human validation according to the '
                        'passage.',
            'answer': 'False'}],
  'ynng': [{'question': 'The author criticises checkbox audits that miss production '
                        'misconfigurations.',
            'answer': 'Yes'},
           {'question': 'The writer believes punitive gatekeeping beats developer empathy.',
            'answer': 'No'},
           {'question': 'The author views equitable cyber resilience as public infrastructure.',
            'answer': 'Yes'},
           {'question': 'The writer supports opaque monitoring without transparency reports.',
            'answer': 'No'},
           {'question': 'The author wants zero-trust to become routine hygiene like patching.',
            'answer': 'Yes'}],
  'matching_headings': [{'paragraph': 'B',
                         'correct': 'ii. Identity hardening and service account risks'},
                        {'paragraph': 'C', 'correct': 'iii. Endpoint telemetry and alert fatigue'},
                        {'paragraph': 'D', 'correct': 'iv. DevSecOps and developer empathy'},
                        {'paragraph': 'E', 'correct': 'v. Supply chain signing and funding gaps'},
                        {'paragraph': 'F', 'correct': 'vi. Privacy limits on security logging'}],
  'headings_pool': ['i. Baroque harp string tariffs',
                    'j. Identity hardening and service account risks',
                    'k. Endpoint telemetry and alert fatigue',
                    'l. DevSecOps and developer empathy',
                    'm. Supply chain signing and funding gaps',
                    'n. Privacy limits on security logging',
                    'o. Desert caravan water rations'],
  'matching_info': [{'question': 'mention of just-in-time elevation for automation accounts',
                     'paragraph': 'B'},
                    {'question': 'reference to graph analytics in security operations centres',
                     'paragraph': 'C'},
                    {'question': 'discussion of secret scanning in pipelines', 'paragraph': 'D'},
                    {'question': 'examples of federal grants for hospitals', 'paragraph': 'E'},
                    {'question': 'a conclusion about leadership turning diagrams into habits',
                     'paragraph': 'G'}],
  'sentence_completion': [{'question': 'Micro-segmentation limits lateral ____ inside networks.',
                           'answer': 'movement'},
                          {'question': 'Phishing-resistant hardware keys strengthen multifactor '
                                       '____.',
                           'answer': 'authentication'},
                          {'question': 'Infrastructure-as-code scanning rejects exposed storage '
                                       '____.',
                           'answer': 'buckets'},
                          {'question': 'Break-glass credentials need sealed procedures tested '
                                       '____.',
                           'answer': 'quarterly'}],
  'summary_completion': [{'question': 'Legacy VPN migration needs inventory of shadow IT ____.',
                          'answer': 'assets'},
                         {'question': 'Ransomware precursors may appear in process ____.',
                          'answer': 'lineage'},
                         {'question': 'Vendors should provide cryptographically signed software '
                                      '____.',
                          'answer': 'artefacts'},
                         {'question': 'Retention limits balance forensics with deletion ____.',
                          'answer': 'obligations'}],
  'table_completion': [{'question': 'Risk policy | Least-privilege grants application ____',
                        'answer': 'access'},
                       {'question': 'SOC challenge | Alert fatigue hides true ____',
                        'answer': 'positives'},
                       {'question': 'Continuity | Identity outages require disaster ____',
                        'answer': 'recovery'}],
  'mcq': [{'question': 'Paragraph A contrasts zero-trust with',
           'options': ['air-gapped perfection',
                       'castle-and-moat perimeter reliance',
                       'unlimited trust inside VPNs',
                       'ban on micro-segmentation'],
           'answer': 'castle-and-moat perimeter reliance'},
          {'question': 'According to paragraph B, service accounts risk',
           'options': ['automatic least privilege',
                       'excessive permissions without just-in-time controls',
                       'no automation',
                       'mandatory hardware keys for humans only'],
           'answer': 'excessive permissions without just-in-time controls'},
          {'question': 'Paragraph D indicates developers accept security when',
           'options': ['autofix integrates into familiar tools',
                       'all releases are blocked',
                       'secrets remain in repos',
                       'containers skip scanning'],
           'answer': 'autofix integrates into familiar tools'},
          {'question': 'Paragraph F mentions works councils negotiating',
           'options': ['monitoring scope for remote staff',
                       'elimination of all logging',
                       'supply chain signing',
                       'insurance premiums only'],
           'answer': 'monitoring scope for remote staff'},
          {'question': 'The final paragraph stresses',
           'options': ['victim blaming in sharing',
                       'sustained leadership attention',
                       'discarding zero-trust after breaches',
                       'ending disaster exercises'],
           'answer': 'sustained leadership attention'}],
  'short_answer': [{'question': 'What model assumes perimeter defences are insufficient?',
                    'answer': 'zero-trust',
                    'word_limit': 1},
                   {'question': 'What east-west traffic pattern does micro-segmentation watch?',
                    'answer': 'anomalous',
                    'word_limit': 1},
                   {'question': 'What documents list software components for supply chains?',
                    'answer': 'bill of materials',
                    'word_limit': 3},
                   {'question': 'What metrics does the author prefer over blocked malware counts?',
                    'answer': 'mean-time-to-contain',
                    'word_limit': 1}]},
 {'quiz_number': 15,
  'title': 'Digital twins in industry',
  'topic_category': 'Technology',
  'paragraphs': {'A': 'Digital twins are virtual replicas of physical assets fed by sensors, '
                      'simulation models, and enterprise data to forecast performance and test '
                      'interventions before costly field changes. Manufacturers mirror production '
                      'lines to identify bottlenecks, predict tool wear, and schedule maintenance '
                      'during planned downtime rather than after catastrophic failures. Utilities '
                      'model substations and pipelines to rehearse storm responses, improving crew '
                      'dispatch when multiple faults coincide across distribution networks. '
                      'Healthcare institutions experiment with organ-level twins personalising '
                      'dosage, though privacy governance for continuous biometric streams remains '
                      'contentious. Successful programmes require disciplined data governance '
                      'aligning measurement units, timestamps, and ownership across traditionally '
                      'siloed departments.',
                 'B': 'Physics-based solvers integrate finite element meshes with real-time '
                      'telemetry, highlighting stress hotspots invisible to routine inspections '
                      'alone. Reduced-order models accelerate computations for control room '
                      'dashboards, trading microscopic fidelity for actionable trend indicators '
                      'operators understand. Calibration drift occurs when sensors age or '
                      'installations shift, producing confident but misleading predictions until '
                      'recalibration campaigns restore fidelity. The author insists human experts '
                      'validate anomalies rather than delegating irreversible shutdown decisions '
                      'entirely to automated thresholds. Without calibration budgets, twins '
                      'degenerate into expensive three-dimensional animations disconnected from '
                      'operational reality. Cross-disciplinary collaboration, sustained funding, '
                      'and careful communication with affected communities remain central to '
                      'credible long-term outcomes.',
                 'C': 'Interoperability standards enable twins to exchange components across '
                      'vendors, preventing proprietary lock-in that duplicates integration effort. '
                      'Semantic ontologies describe equipment classes consistently so maintenance '
                      'histories attach to correct virtual nodes automatically. Small firms access '
                      'cloud-hosted twin platforms via subscription, lowering capital barriers yet '
                      'raising dependency on external uptime guarantees. Cybersecurity reviews '
                      'treat twins as high-value targets because manipulating virtual models could '
                      'mask physical defects or trigger unsafe commands. The writer advocates '
                      'mutual authentication between field gateways and cloud orchestration '
                      'layers. Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'D': 'Urban planners build city-scale twins simulating traffic, flooding, and '
                      'energy demand under climate scenarios for infrastructure investment '
                      'debates. Citizen engagement workshops visualise proposed transit lines, '
                      'translating abstract models into maps residents can critique during '
                      'consultations. Equity analysts examine whether twin insights redirect '
                      'investment toward affluent districts already rich in sensors, neglecting '
                      'underserved neighbourhoods. Open data mandates may require anonymised '
                      'aggregates while protecting individual mobility traces collected from '
                      'mobile networks. The author contends participatory design prevents twins '
                      'from becoming technocratic tools justifying predetermined megaprojects. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'E': 'Product lifecycle twins follow aircraft and wind turbines from design '
                      'through decommissioning, compiling fatigue records for resale markets. '
                      'Regulators may accept simulation evidence reducing physical testing hours '
                      'when validation protocols demonstrate correlation with destructive trials. '
                      'Secondary markets for used equipment rely on tamper-evident logs proving '
                      'maintenance compliance across ownership transfers. Lawyers draft liability '
                      'clauses allocating responsibility when twin recommendations contribute to '
                      'accidents despite following vendor defaults. The writer believes '
                      'transparent audit trails build trust across supply chains more than '
                      'marketing claims of digital transformation. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes.',
                 'F': 'Workforce training uses immersive interfaces linked to twins, allowing '
                      'apprentices to practice hazardous procedures virtually before touching live '
                      'machinery. Unions negotiate how performance metrics derived from twins '
                      'influence evaluations, resisting surveillance narratives focused solely on '
                      'efficiency extraction. Educational partnerships align vocational curricula '
                      'with skills needed to maintain sensor networks and interpret model '
                      'uncertainty bands. Demographic shifts toward retiring specialists make '
                      'knowledge capture into twins urgent for preserving tacit troubleshooting '
                      'expertise. The author supports co-design with workers so tools augment '
                      'craft rather than discredit experiential judgment. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes.',
                 'G': 'Next-generation twins may close loops automatically adjusting setpoints '
                      'within safety envelopes certified by regulators. Ethics boards will review '
                      'autonomous optimisation affecting emissions, water use, and neighbourhood '
                      'noise simultaneously. The writer foresees widespread adoption when '
                      'organisations publish case studies quantifying return on investment beyond '
                      'pilot hype. Cross-industry learning forums can disseminate failure stories '
                      'as openly as success metrics, accelerating maturity. Digital twins '
                      'ultimately succeed when they strengthen physical systems people depend on, '
                      'not when they merely decorate executive presentations. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.'},
  'tfng': [{'question': 'Digital twins combine sensor data with simulation models.',
            'answer': 'True'},
           {'question': 'All healthcare twins operate without privacy concerns.',
            'answer': 'False'},
           {'question': 'Every small firm owns proprietary twin software outright.',
            'answer': 'Not Given'},
           {'question': 'Calibration drift can make predictions misleading.', 'answer': 'True'},
           {'question': 'The passage states regulators never accept simulation evidence.',
            'answer': 'False'}],
  'ynng': [{'question': 'The author insists experts validate anomalies before irreversible '
                        'shutdowns.',
            'answer': 'Yes'},
           {'question': 'The writer believes twins should replace worker judgment entirely.',
            'answer': 'No'},
           {'question': 'The author supports participatory design to avoid technocratic bias.',
            'answer': 'Yes'},
           {'question': 'The writer thinks audit trails are less important than marketing.',
            'answer': 'No'},
           {'question': 'The author wants twins to strengthen real physical systems.',
            'answer': 'Yes'}],
  'matching_headings': [{'paragraph': 'B',
                         'correct': 'ii. Solvers, reduced models, and calibration drift'},
                        {'paragraph': 'C',
                         'correct': 'iii. Ontologies, subscriptions, and twin cybersecurity'},
                        {'paragraph': 'D',
                         'correct': 'iv. City-scale simulation and equity concerns'},
                        {'paragraph': 'E',
                         'correct': 'v. Lifecycle records and liability allocation'},
                        {'paragraph': 'F',
                         'correct': 'vi. Workforce training and union negotiation'}],
  'headings_pool': ['i. Medieval spice route tolls',
                    'j. Solvers, reduced models, and calibration drift',
                    'k. Ontologies, subscriptions, and twin cybersecurity',
                    'l. City-scale simulation and equity concerns',
                    'm. Lifecycle records and liability allocation',
                    'n. Workforce training and union negotiation',
                    'o. Ancient amphora shipping lanes'],
  'matching_info': [{'question': 'mention of reduced-order models for dashboards',
                     'paragraph': 'B'},
                    {'question': 'reference to semantic ontologies for equipment classes',
                     'paragraph': 'C'},
                    {'question': 'discussion of citizen workshops for transit proposals',
                     'paragraph': 'D'},
                    {'question': 'examples of tamper-evident maintenance logs', 'paragraph': 'E'},
                    {'question': 'a conclusion about quantified return on investment',
                     'paragraph': 'G'}],
  'sentence_completion': [{'question': 'Finite element meshes highlight stress ____.',
                           'answer': 'hotspots'},
                          {'question': 'Cloud subscriptions lower capital ____ for small firms.',
                           'answer': 'barriers'},
                          {'question': 'Immersive training lets apprentices practice ____ '
                                       'procedures.',
                           'answer': 'hazardous'},
                          {'question': 'Autonomous setpoints must stay within safety ____.',
                           'answer': 'envelopes'}],
  'summary_completion': [{'question': 'Utilities rehearse storm responses on virtual ____.',
                          'answer': 'pipelines'},
                         {'question': 'Open data may protect mobility traces via ____.',
                          'answer': 'anonymisation'},
                         {'question': 'Regulators may accept simulation when validation correlates '
                                      'with ____ trials.',
                          'answer': 'destructive'},
                         {'question': 'Cross-industry forums should share failure ____ openly.',
                          'answer': 'stories'}],
  'table_completion': [{'question': 'Data issue | Misaligned timestamps break twin ____',
                        'answer': 'fidelity'},
                       {'question': 'Urban risk | Sensor-rich districts may attract '
                                    'disproportionate ____',
                        'answer': 'investment'},
                       {'question': 'Workforce | Retiring specialists threaten tacit ____',
                        'answer': 'expertise'}],
  'mcq': [{'question': 'Paragraph A emphasises twins help schedule maintenance during',
           'options': ['random failures only',
                       'planned downtime',
                       'marketing events',
                       'regulatory bans'],
           'answer': 'planned downtime'},
          {'question': 'According to paragraph B, twins fail when',
           'options': ['calibration is funded',
                       'sensors drift without recalibration',
                       'humans validate anomalies',
                       'solvers exist'],
           'answer': 'sensors drift without recalibration'},
          {'question': 'Paragraph D warns twins could neglect',
           'options': ['affluent districts',
                       'underserved neighbourhoods with fewer sensors',
                       'citizen workshops',
                       'climate scenarios'],
           'answer': 'underserved neighbourhoods with fewer sensors'},
          {'question': 'Paragraph F indicates unions negotiate metrics affecting',
           'options': ['only cloud uptime',
                       'evaluations derived from twin data',
                       'semantic ontologies',
                       'aircraft resale'],
           'answer': 'evaluations derived from twin data'},
          {'question': 'The final paragraph says success requires',
           'options': ['decorating executive slides only',
                       'strengthening physical systems people depend on',
                       'hiding failure stories',
                       'ending ethics boards'],
           'answer': 'strengthening physical systems people depend on'}],
  'short_answer': [{'question': 'What numerical method integrates meshes with telemetry?',
                    'answer': 'finite element',
                    'word_limit': 2},
                   {'question': 'What drift makes confident predictions misleading?',
                    'answer': 'calibration',
                    'word_limit': 1},
                   {'question': 'What interfaces help apprentices practice safely?',
                    'answer': 'immersive',
                    'word_limit': 1},
                   {'question': 'What boards will review autonomous optimisation trade-offs?',
                    'answer': 'ethics',
                    'word_limit': 1}]},
 {'quiz_number': 16,
  'title': 'Autonomous vehicle policy',
  'topic_category': 'Technology',
  'paragraphs': {'A': 'Autonomous vehicles combine perception sensors, high-definition maps, and '
                      'planning algorithms to navigate traffic with reduced human intervention '
                      'across operational design domains. Manufacturers classify automation '
                      'levels, distinguishing driver assistance from systems capable of monitoring '
                      'environments without continuous human control in defined conditions. Pilot '
                      'deployments in geofenced districts test robotaxi services, delivery pods, '
                      'and shuttle routes connecting transit hubs with suburban employment zones. '
                      'Incident reporting databases aggregate disengagements and collisions, '
                      'informing regulators setting performance standards before nationwide '
                      'approvals. Public acceptance hinges on transparent safety evidence rather '
                      'than marketing demonstrations on closed courses alone. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes.',
                 'B': 'Liability frameworks debate whether software vendors, fleet operators, or '
                      'human supervisors bear responsibility when automation fails during edge '
                      'cases. Comparative negligence statutes written for human drivers require '
                      'reinterpretation for decisions made in milliseconds by opaque neural '
                      'networks. Insurance products experiment with usage-based premiums tracking '
                      'operational design domain adherence and maintenance of sensor calibrations. '
                      'The author argues clarity prevents protracted litigation that could stall '
                      'beneficial safety technologies alongside immature deployments. '
                      'International harmonisation of crash data formats would accelerate learning '
                      'across borders currently siloed by proprietary confidentiality claims. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'C': 'Cybersecurity rules mandate over-the-air update authentication and '
                      'intrusion detection protecting steering and braking actuators from remote '
                      'hijacking. Penetration testers demonstrate vulnerabilities in telematics '
                      'modules, prompting coordinated disclosure programmes rewarding independent '
                      'researchers. Fleet operators segment wireless networks isolating passenger '
                      'infotainment from safety-critical controller area network gateways. Supply '
                      'chain audits verify firmware signatures on components sourced globally '
                      'under time pressure to launch commercial services. The writer believes '
                      'security cannot be retrofitted after vehicles mass-deploy without costly '
                      'recalls undermining public trust. Cross-disciplinary collaboration, '
                      'sustained funding, and careful communication with affected communities '
                      'remain central to credible long-term outcomes. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes.',
                 'D': 'Urban planners reconsider curb management as drop-off patterns shift and '
                      'empty vehicles cruise awaiting passengers. Congestion pricing models may '
                      'account for zero-occupancy miles unless regulations require remote parking '
                      'between fares. Accessibility advocates demand wheelchair-compatible designs '
                      'and audio interfaces serving visually impaired riders equitably. Labour '
                      'organisations protest job displacement among professional drivers, seeking '
                      'retraining funds tied to permit approvals. The author contends transport '
                      'equity assessments should precede exclusive partnerships granting operators '
                      'monopoly routes. Cross-disciplinary collaboration, sustained funding, and '
                      'careful communication with affected communities remain central to credible '
                      'long-term outcomes. Policymakers increasingly demand reproducible evidence, '
                      'open data, and independent evaluation before scaling interventions beyond '
                      'controlled pilot settings.',
                 'E': 'Environmental analyses compare lifecycle emissions of autonomous electric '
                      'fleets against conventional ownership, including battery production and '
                      'grid carbon intensity. Shared mobility could reduce private car purchases, '
                      'yet induced demand from cheaper trips might increase total vehicle '
                      'kilometres travelled. Charging infrastructure planning must coordinate with '
                      'utilities forecasting evening peaks when fleets return to depots '
                      'simultaneously. Recycling policies for sensor-rich vehicles remain immature '
                      'compared with powertrain-focused end-of-life regulations. The writer urges '
                      'holistic modelling rather than assuming automation automatically delivers '
                      'sustainability benefits. Cross-disciplinary collaboration, sustained '
                      'funding, and careful communication with affected communities remain central '
                      'to credible long-term outcomes.',
                 'F': 'Ethical programming addresses trolley-problem narratives, prioritising harm '
                      'reduction strategies validated through multidisciplinary review boards. '
                      'Transparency about value choices embedded in collision avoidance policies '
                      'may matter more than hypothetical extreme scenarios. Pedestrian expectation '
                      'studies reveal confusion when mixed traffic includes silent electric '
                      'autonomous vehicles approaching intersections. Standardised external sound '
                      'and lighting cues could communicate intent without overwhelming urban noise '
                      'environments. The author supports public deliberation on acceptable risk '
                      'budgets rather than secret corporate tuning alone. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes. Policymakers '
                      'increasingly demand reproducible evidence, open data, and independent '
                      'evaluation before scaling interventions beyond controlled pilot settings.',
                 'G': 'Gradual regulatory pathways may require years of supervised expansion '
                      'before unrestricted cross-country travel becomes feasible. Interstate '
                      'commercial trucking pilots focus on highway segments with minimal complex '
                      'urban interactions initially. The writer expects policy to co-evolve with '
                      'demonstrated safety margins, avoiding both blanket bans and premature '
                      'deregulation. Investment in digital infrastructure such as lane markings '
                      'and connectivity will determine which regions benefit first. Ultimately, '
                      'autonomous mobility should integrate with public transit goals rather than '
                      'replicating solo car dependence at algorithmic scale. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes.'},
  'tfng': [{'question': 'Operational design domains limit where automation may operate.',
            'answer': 'True'},
           {'question': 'All countries use identical liability laws for neural network decisions.',
            'answer': 'False'},
           {'question': 'The passage confirms nationwide robotaxi approval everywhere.',
            'answer': 'Not Given'},
           {'question': 'Cybersecurity guidance includes authenticated over-the-air updates.',
            'answer': 'True'},
           {'question': 'Automation always reduces total vehicle kilometres according to the '
                        'passage.',
            'answer': 'False'}],
  'ynng': [{'question': 'The author wants liability clarity to avoid litigation stalls.',
            'answer': 'Yes'},
           {'question': 'The writer believes security can wait until after mass deployment.',
            'answer': 'No'},
           {'question': 'The author supports transport equity assessments before monopolies.',
            'answer': 'Yes'},
           {'question': 'The writer claims automation automatically guarantees sustainability.',
            'answer': 'No'},
           {'question': 'The author favours public deliberation on risk budgets.',
            'answer': 'Yes'}],
  'matching_headings': [{'paragraph': 'B',
                         'correct': 'ii. Liability, insurance, and crash data formats'},
                        {'paragraph': 'C',
                         'correct': 'iii. Cybersecurity and firmware supply chains'},
                        {'paragraph': 'D', 'correct': 'iv. Curb space, labour, and accessibility'},
                        {'paragraph': 'E', 'correct': 'v. Lifecycle emissions and induced demand'},
                        {'paragraph': 'F',
                         'correct': 'vi. Ethical harm reduction and pedestrian cues'}],
  'headings_pool': ['i. Renaissance coin debasement scandals',
                    'j. Liability, insurance, and crash data formats',
                    'k. Cybersecurity and firmware supply chains',
                    'l. Curb space, labour, and accessibility',
                    'm. Lifecycle emissions and induced demand',
                    'n. Ethical harm reduction and pedestrian cues',
                    'o. Victorian tea auction rituals'],
  'matching_info': [{'question': 'discussion of usage-based insurance tracking domain adherence',
                     'paragraph': 'B'},
                    {'question': 'reference to penetration testing of telematics',
                     'paragraph': 'C'},
                    {'question': 'mention of congestion from zero-occupancy cruising',
                     'paragraph': 'D'},
                    {'question': 'analysis of induced demand increasing kilometres travelled',
                     'paragraph': 'E'},
                    {'question': 'a conclusion integrating autonomy with public transit goals',
                     'paragraph': 'G'}],
  'sentence_completion': [{'question': 'High-definition maps support navigation within operational '
                                       'design ____.',
                           'answer': 'domains'},
                          {'question': 'Firmware signatures verify globally sourced ____.',
                           'answer': 'components'},
                          {'question': 'Wheelchair-compatible designs serve accessibility ____.',
                           'answer': 'advocates'},
                          {'question': 'External sound cues can communicate vehicle ____.',
                           'answer': 'intent'}],
  'summary_completion': [{'question': 'Incident databases track disengagements and ____.',
                          'answer': 'collisions'},
                         {'question': 'Controller area network gateways separate infotainment from '
                                      '____ systems.',
                          'answer': 'safety-critical'},
                         {'question': 'Evening charging peaks require utility ____ forecasts.',
                          'answer': 'forecasting'},
                         {'question': 'Trucking pilots begin on highway ____ with fewer urban '
                                      'interactions.',
                          'answer': 'segments'}],
  'table_completion': [{'question': 'Policy gap | Neural networks complicate comparative ____ '
                                    'statutes',
                        'answer': 'negligence'},
                       {'question': 'Urban issue | Empty vehicles may cruise awaiting ____',
                        'answer': 'passengers'},
                       {'question': 'Ethics | Review boards examine harm ____ strategies',
                        'answer': 'reduction'}],
  'mcq': [{'question': 'Paragraph A says public acceptance depends on',
           'options': ['closed course demos alone',
                       'transparent safety evidence',
                       'banning reporting databases',
                       'ignoring automation levels'],
           'answer': 'transparent safety evidence'},
          {'question': 'According to paragraph C, fleet operators isolate',
           'options': ['passenger infotainment from safety networks',
                       'all wireless communication entirely',
                       'only human drivers',
                       'insurance products'],
           'answer': 'passenger infotainment from safety networks'},
          {'question': 'Paragraph E warns cheaper trips might',
           'options': ['eliminate all charging needs',
                       'increase total kilometres travelled',
                       'ban electric fleets',
                       'end battery production'],
           'answer': 'increase total kilometres travelled'},
          {'question': 'Paragraph F suggests pedestrians struggle with',
           'options': ['loud combustion engines only',
                       'silent electric autonomous approaches',
                       'standardised lighting bans',
                       'harm reduction boards'],
           'answer': 'silent electric autonomous approaches'},
          {'question': 'The final paragraph urges autonomy to',
           'options': ['replace all transit',
                       'integrate with public transit goals',
                       'ignore digital infrastructure',
                       'mandate solo car use'],
           'answer': 'integrate with public transit goals'}],
  'short_answer': [{'question': 'What databases record automation disengagements?',
                    'answer': 'incident',
                    'word_limit': 1},
                   {'question': 'What updates require authentication against hijacking?',
                    'answer': 'over-the-air',
                    'word_limit': 2},
                   {'question': 'What pricing may penalise zero-occupancy miles?',
                    'answer': 'congestion',
                    'word_limit': 1},
                   {'question': 'What trucking routes start with simpler highway segments?',
                    'answer': 'interstate',
                    'word_limit': 1}]},
 {'quiz_number': 17,
  'title': 'Green data centre design',
  'topic_category': 'Technology',
  'paragraphs': {'A': 'Data centres house servers, storage, and networking equipment consuming '
                      'enormous electricity for computation and cooling, prompting designers to '
                      'pursue energy and water efficiency. Hyperscale operators locate facilities '
                      'near renewable generation or cool climates to reduce carbon intensity and '
                      'mechanical refrigeration loads. Power usage effectiveness metrics compare '
                      'total facility demand to information technology load, guiding benchmarking '
                      'though imperfectly capturing renewable matching. Edge sites proliferate for '
                      'latency-sensitive applications, complicating centralised sustainability '
                      'reporting across distributed footprints. Regulators increasingly require '
                      'disclosure of emissions analogous to other large industrial consumers. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'B': 'Liquid cooling circulates dielectric fluids or water through cold plates '
                      'contacting processors, enabling higher rack densities than air alone. '
                      'Immersion tanks submerge boards in non-conductive oils, eliminating fan '
                      'power yet complicating maintenance procedures technicians must learn. Heat '
                      'reuse projects pipe waste warmth into district heating networks supplying '
                      'apartments near campus-scale server farms. The author notes reuse economics '
                      'depend on local demand seasons aligning with steady server loads '
                      'year-round. Without adjacent heat customers, exhaust merely disperses, '
                      'wasting thermodynamic opportunity despite efficient onsite cooling. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'C': 'Renewable power purchase agreements contract wind or solar output, while '
                      'battery storage smooths intermittency affecting uptime service level '
                      'agreements. Some operators schedule batch workloads during surplus '
                      'generation hours, using software orchestration to chase cleaner '
                      'electricity. Grid operators worry large flexible loads may destabilise '
                      'networks if synchronised switching creates ramping shocks. Transparent '
                      'communication with utilities coordinates demand response participation '
                      'compensating curtailed compute during peak pricing events. The writer '
                      'advocates treating data centres as grid partners, not isolated baseload '
                      'parasites. Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes. Cross-disciplinary collaboration, sustained funding, '
                      'and careful communication with affected communities remain central to '
                      'credible long-term outcomes.',
                 'D': 'Water conservation matters in drought-prone regions where evaporative '
                      'cooling towers withdraw millions of litres annually. Closed-loop systems '
                      'and adiabatic economisers trade capital expense for reduced freshwater '
                      'stress affecting neighbouring agriculture. Communities negotiate siting '
                      'permits demanding water budgets and habitat protections near aquifer '
                      'recharge zones. Environmental justice advocates highlight disproportionate '
                      'impacts when facilities cluster beside low-income towns reliant on fragile '
                      'supplies. The author contends siting policy must integrate hydrology, not '
                      'only tax incentives offered by eager municipalities. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes. Policymakers '
                      'increasingly demand reproducible evidence, open data, and independent '
                      'evaluation before scaling interventions beyond controlled pilot settings.',
                 'E': 'Hardware efficiency improvements from specialised accelerators running '
                      'artificial intelligence workloads reduce energy per inference operation. '
                      'Yet aggregate demand may grow faster than per-chip gains, echoing rebound '
                      'effects seen in other efficiency domains. Circular economy programmes '
                      'refurbish retired servers for secondary markets, extending life while '
                      'ensuring secure data destruction. Design for disassembly remains rare when '
                      'rapid obsolescence favours sealed proprietary modules difficult to recycle '
                      'responsibly. The writer supports mandatory reporting of embodied emissions '
                      'in procurement alongside operational carbon metrics. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'F': 'Certification schemes rate buildings on energy, water, and renewable '
                      'integration, though greenwashing concerns persist when operators '
                      'cherry-pick favourable sites. Third-party audits verify claims before '
                      'investors allocate environmental, social, and governance funds toward '
                      'digital infrastructure. Open standards for server efficiency labels help '
                      'buyers compare equipment beyond marketing thermal design power figures '
                      'alone. Workforce development trains facility engineers in hybrid cooling '
                      'architectures spanning electrical and mechanical disciplines. The author '
                      'believes skilled operators unlock savings invisible in blueprint efficiency '
                      'ratings alone. Cross-disciplinary collaboration, sustained funding, and '
                      'careful communication with affected communities remain central to credible '
                      'long-term outcomes. Cross-disciplinary collaboration, sustained funding, '
                      'and careful communication with affected communities remain central to '
                      'credible long-term outcomes.',
                 'G': 'Future facilities may integrate on-site microgrids with fuel cells or '
                      'geothermal loops where geology permits stable low-carbon heat rejection. '
                      'Policy roadmaps setting science-based targets could align industry growth '
                      'with national net-zero timelines without halting digital transformation. '
                      'The writer expects transparency and grid partnership to define leadership '
                      'more than vanity architecture showcasing cosmetic green roofs. '
                      'International cooperation sharing best practices prevents reinventing '
                      'inefficient cooling in emerging markets building first-generation clouds. '
                      'Sustainable data centres ultimately serve society better when they deliver '
                      'digital services without imposing hidden environmental debts on neighbours. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.'},
  'tfng': [{'question': 'Power usage effectiveness relates total facility power to IT load.',
            'answer': 'True'},
           {'question': 'Immersion cooling always simplifies maintenance without training.',
            'answer': 'False'},
           {'question': 'Every data centre sells waste heat to district networks profitably.',
            'answer': 'Not Given'},
           {'question': 'Batch scheduling can align compute with surplus renewables.',
            'answer': 'True'},
           {'question': 'The passage states rebound effects never occur in data centres.',
            'answer': 'False'}],
  'ynng': [{'question': 'The author says heat reuse needs aligned local demand seasons.',
            'answer': 'Yes'},
           {'question': 'The writer believes facilities should ignore utility coordination.',
            'answer': 'No'},
           {'question': 'The author highlights hydrology in siting beyond tax incentives.',
            'answer': 'Yes'},
           {'question': 'The writer thinks operational metrics alone suffice without embodied '
                        'emissions.',
            'answer': 'No'},
           {'question': 'The author wants data centres as grid partners not parasites.',
            'answer': 'Yes'}],
  'matching_headings': [{'paragraph': 'B', 'correct': 'ii. Liquid cooling and district heat reuse'},
                        {'paragraph': 'C',
                         'correct': 'iii. Renewables, batteries, and demand response'},
                        {'paragraph': 'D', 'correct': 'iv. Water stress and environmental justice'},
                        {'paragraph': 'E',
                         'correct': 'v. Accelerators, rebound, and refurbishment'},
                        {'paragraph': 'F',
                         'correct': 'vi. Certifications, audits, and workforce skills'}],
  'headings_pool': ['i. Baroque lace export quotas',
                    'j. Liquid cooling and district heat reuse',
                    'k. Renewables, batteries, and demand response',
                    'l. Water stress and environmental justice',
                    'm. Accelerators, rebound, and refurbishment',
                    'n. Certifications, audits, and workforce skills',
                    'o. Ancient chariot wheel spokes'],
  'matching_info': [{'question': 'mention of immersion tanks with non-conductive oils',
                     'paragraph': 'B'},
                    {'question': 'reference to workloads scheduled during surplus renewables',
                     'paragraph': 'C'},
                    {'question': 'discussion of evaporative towers in drought-prone regions',
                     'paragraph': 'D'},
                    {'question': 'examples of refurbished servers in secondary markets',
                     'paragraph': 'E'},
                    {'question': 'a conclusion about avoiding hidden environmental debts',
                     'paragraph': 'G'}],
  'sentence_completion': [{'question': 'Dielectric fluids enable liquid ____ through cold plates.',
                           'answer': 'cooling'},
                          {'question': 'Battery storage smooths renewable ____.',
                           'answer': 'intermittency'},
                          {'question': 'Adiabatic economisers reduce freshwater ____ in cooling.',
                           'answer': 'stress'},
                          {'question': 'Microgrids may integrate fuel cells or ____ loops.',
                           'answer': 'geothermal'}],
  'summary_completion': [{'question': 'Hyperscale sites seek cool climates to cut refrigeration '
                                      '____.',
                          'answer': 'loads'},
                         {'question': 'Demand response compensates curtailed compute during peak '
                                      '____.',
                          'answer': 'pricing'},
                         {'question': 'Secure data destruction precedes server ____.',
                          'answer': 'refurbishment'},
                         {'question': 'Science-based targets align growth with net-zero ____.',
                          'answer': 'timelines'}],
  'table_completion': [{'question': 'Metric | Power usage effectiveness benchmarks facility ____',
                        'answer': 'efficiency'},
                       {'question': 'Risk | Synchronised load switching may shock the ____',
                        'answer': 'grid'},
                       {'question': 'Procurement | Buyers need labels beyond thermal design ____',
                        'answer': 'power'}],
  'mcq': [{'question': 'Paragraph A notes edge proliferation complicates',
           'options': ['centralised sustainability reporting',
                       'liquid cooling adoption',
                       'renewable bans',
                       'district heating'],
           'answer': 'centralised sustainability reporting'},
          {'question': 'According to paragraph B, heat reuse fails without',
           'options': ['adjacent heat customers',
                       'immersion oil bans',
                       'more fans',
                       'higher PUE only'],
           'answer': 'adjacent heat customers'},
          {'question': 'Paragraph D links siting to',
           'options': ['only tax incentives',
                       'hydrology and fragile water supplies',
                       'AI accelerators only',
                       'chariot design'],
           'answer': 'hydrology and fragile water supplies'},
          {'question': 'Paragraph E describes rebound when',
           'options': ['demand grows faster than per-chip gains',
                       'accelerators are illegal',
                       'servers never retire',
                       'PUE equals zero'],
           'answer': 'demand grows faster than per-chip gains'},
          {'question': 'The final paragraph emphasises leadership through',
           'options': ['cosmetic green roofs only',
                       'transparency and grid partnership',
                       'ignoring emerging markets',
                       'ending digital services'],
           'answer': 'transparency and grid partnership'}],
  'short_answer': [{'question': 'What metric compares total power to IT equipment load?',
                    'answer': 'PUE',
                    'word_limit': 1},
                   {'question': 'What cooling submerges boards in non-conductive oil?',
                    'answer': 'immersion',
                    'word_limit': 1},
                   {'question': 'What agreements contract wind or solar for facilities?',
                    'answer': 'power purchase',
                    'word_limit': 2},
                   {'question': 'What justice issue arises near drought-prone siting?',
                    'answer': 'environmental',
                    'word_limit': 1}]},
 {'quiz_number': 18,
  'title': 'Biometric authentication limits',
  'topic_category': 'Technology',
  'paragraphs': {'A': 'Biometric authentication uses physiological or behavioural traits such as '
                      'fingerprints, facial geometry, or voice patterns to verify identity during '
                      'device unlock and border crossings. Convenience attracts adoption because '
                      'users need not memorise complex passwords, yet biometric templates differ '
                      'from secrets because individuals cannot rotate their faces after breaches. '
                      'Presentation attack detection attempts to distinguish live subjects from '
                      'photographs, masks, or synthetic deepfakes projected toward sensors. '
                      'Regulators classify biometrics as sensitive personal data requiring '
                      'explicit consent and purpose limitation in many jurisdictions. Security '
                      'architects recommend pairing biometrics with possession factors so stolen '
                      'templates alone cannot grant access.',
                 'B': 'False acceptance and false rejection rates trade security against '
                      'usability, especially for ageing populations whose fingerprints wear or '
                      'voices change after illness. Laboratory evaluations under ideal lighting '
                      'misrepresent performance on dark-skinned individuals when training datasets '
                      'underrepresent demographic diversity. Independent audits publish '
                      'disaggregated metrics pressuring vendors to improve equity before public '
                      'sector procurement. The author argues transparency reports should become '
                      'mandatory, not voluntary marketing appendices buried in technical manuals. '
                      'Without disaggregated testing, systems may deploy widely while '
                      'systematically disadvantaging marginalised communities. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes.',
                 'C': 'Centralised template databases create honeypots attracting nation-state '
                      'espionage and criminal resale on underground markets. On-device processing '
                      'stores embeddings locally, reducing breach blast radius yet complicating '
                      'cross-device account recovery workflows. Cryptographic cancellable '
                      'biometrics transform raw samples into revocable tokens, a research area '
                      'slowly maturing into standards. Privacy advocates prefer decentralised '
                      'models giving users wallet control over when attributes are disclosed. The '
                      'writer cautions that local storage alone does not prevent coercion if '
                      'individuals are forced to unlock devices. Cross-disciplinary collaboration, '
                      'sustained funding, and careful communication with affected communities '
                      'remain central to credible long-term outcomes. Policymakers increasingly '
                      'demand reproducible evidence, open data, and independent evaluation before '
                      'scaling interventions beyond controlled pilot settings.',
                 'D': 'Workplace monitoring using facial recognition for attendance tracking '
                      'sparked union grievances citing chilling effects on organising. Retail '
                      'analytics counting shoppers by age and gender blur authentication with '
                      'surveillance capitalism revenue models. Courts wrestle with compelled '
                      'decryption precedents when biometrics unlock phones subject to search '
                      'warrants. Legal scholars propose higher evidentiary thresholds before '
                      'biometric dragnet searches of public crowds. The author believes '
                      'proportionality principles should limit biometric collection to narrowly '
                      'defined high-risk scenarios. Cross-disciplinary collaboration, sustained '
                      'funding, and careful communication with affected communities remain central '
                      'to credible long-term outcomes. Policymakers increasingly demand '
                      'reproducible evidence, open data, and independent evaluation before scaling '
                      'interventions beyond controlled pilot settings.',
                 'E': 'Healthcare settings adopt palm-vein scanners reducing contact infection '
                      'risks, integrating with electronic records under strict role-based access. '
                      'Clinicians worry mistaken matches could merge incompatible blood types, '
                      'demanding fail-safe secondary checks for critical actions. Emergency '
                      'override credentials remain necessary when injuries prevent scanning burned '
                      'or bandaged anatomical sites. Audit logs must record who accessed records '
                      'without exposing patient trajectories to curious insiders. The writer '
                      'supports clinical workflows that treat biometrics as assistive, not sole '
                      'arbiters of identity. Cross-disciplinary collaboration, sustained funding, '
                      'and careful communication with affected communities remain central to '
                      'credible long-term outcomes. Policymakers increasingly demand reproducible '
                      'evidence, open data, and independent evaluation before scaling '
                      'interventions beyond controlled pilot settings.',
                 'F': 'Cross-border travellers encounter varying retention policies for iris '
                      'scans, complicating data deletion requests after trips conclude. Airlines '
                      'trial biometric boarding gates accelerating queues while privacy officers '
                      "negotiate data minimisation schedules. Children's biometrics raise "
                      'developmental consent questions because traits evolve during growth, '
                      'invalidating earlier templates. Educational deployments for cafeteria '
                      'payments require parental opt-in and alternative cash-equivalent options. '
                      'The author contends schools must not normalise ubiquitous biometric '
                      'tracking as precondition for basic services. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes. Policymakers '
                      'increasingly demand reproducible evidence, open data, and independent '
                      'evaluation before scaling interventions beyond controlled pilot settings.',
                 'G': 'Future standards may combine liveness detection with hardware-backed secure '
                      'elements resisting remote template extraction. Multilateral agreements '
                      'could harmonise deletion timelines and ban indiscriminate mass '
                      'identification in public squares. The writer expects biometric adoption to '
                      'persist where benefits are clear, but not as universal replacement for all '
                      'authentication. Policy literacy campaigns should explain limits alongside '
                      'convenience marketing on consumer packaging. Responsible deployment '
                      'recognises bodies are not passwords and demands governance matching that '
                      'reality. Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes. Policymakers increasingly demand reproducible evidence, '
                      'open data, and independent evaluation before scaling interventions beyond '
                      'controlled pilot settings.'},
  'tfng': [{'question': 'Users cannot change biometric traits easily after template theft.',
            'answer': 'True'},
           {'question': 'All vendors publish disaggregated fairness audits mandatorily.',
            'answer': 'False'},
           {'question': 'On-device storage eliminates all coercion risks.', 'answer': 'False'},
           {'question': 'Presentation attacks include photographs and synthetic deepfakes.',
            'answer': 'True'},
           {'question': 'The passage states every school mandates biometric cafeteria payments.',
            'answer': 'Not Given'}],
  'ynng': [{'question': 'The author wants mandatory transparency on demographic performance.',
            'answer': 'Yes'},
           {'question': 'The writer believes biometrics alone should govern critical clinical '
                        'actions.',
            'answer': 'No'},
           {'question': 'The author supports proportionality limiting mass public identification.',
            'answer': 'Yes'},
           {'question': 'The writer thinks local storage fully prevents coercion concerns.',
            'answer': 'No'},
           {'question': 'The author rejects normalising biometrics for basic school services.',
            'answer': 'Yes'}],
  'matching_headings': [{'paragraph': 'B',
                         'correct': 'ii. Error trade-offs and demographic audits'},
                        {'paragraph': 'C',
                         'correct': 'iii. Central databases versus cancellable tokens'},
                        {'paragraph': 'D',
                         'correct': 'iv. Workplace surveillance and legal proportionality'},
                        {'paragraph': 'E',
                         'correct': 'v. Healthcare scanners and emergency overrides'},
                        {'paragraph': 'F',
                         'correct': "vi. Travel retention and children's consent"}],
  'headings_pool': ['i. Medieval tapestry loom guilds',
                    'j. Error trade-offs and demographic audits',
                    'k. Central databases versus cancellable tokens',
                    'l. Workplace surveillance and legal proportionality',
                    'm. Healthcare scanners and emergency overrides',
                    "n. Travel retention and children's consent",
                    'o. Ancient aqueduct valve design'],
  'matching_info': [{'question': 'reference to disaggregated public sector procurement metrics',
                     'paragraph': 'B'},
                    {'question': 'discussion of revocable cryptographic tokens', 'paragraph': 'C'},
                    {'question': 'examples of union grievances on attendance tracking',
                     'paragraph': 'D'},
                    {'question': 'mention of palm-vein scanners in hospitals', 'paragraph': 'E'},
                    {'question': 'a conclusion that bodies are not passwords', 'paragraph': 'G'}],
  'sentence_completion': [{'question': 'Presentation attack detection targets photos, masks, and '
                                       '____.',
                           'answer': 'deepfakes'},
                          {'question': 'False acceptance trades off against false ____ rates.',
                           'answer': 'rejection'},
                          {'question': 'Emergency overrides help when anatomy is bandaged or ____.',
                           'answer': 'burned'},
                          {'question': 'Secure elements resist remote template ____.',
                           'answer': 'extraction'}],
  'summary_completion': [{'question': 'Regulators may require explicit consent for sensitive '
                                      'personal ____.',
                          'answer': 'data'},
                         {'question': 'Cancellable biometrics create revocable ____ from raw '
                                      'samples.',
                          'answer': 'tokens'},
                         {'question': 'Airlines negotiate data minimisation for boarding ____.',
                          'answer': 'gates'},
                         {'question': 'Harmonised policies could ban indiscriminate mass ____ in '
                                      'public squares.',
                          'answer': 'identification'}],
  'table_completion': [{'question': 'Security | Pair biometrics with possession ____',
                        'answer': 'factors'},
                       {'question': 'Retail risk | Analytics blur authentication with surveillance '
                                    '____',
                        'answer': 'capitalism'},
                       {'question': 'Education | Parents need cash-equivalent ____',
                        'answer': 'options'}],
  'mcq': [{'question': 'Paragraph A recommends combining biometrics with',
           'options': ['nothing else',
                       'possession factors',
                       'public template databases only',
                       'mandatory school tracking'],
           'answer': 'possession factors'},
          {'question': 'According to paragraph B, ideal lab lighting may hide',
           'options': ['perfect equity',
                       'poor performance on underrepresented groups',
                       'any false rejects',
                       'hardware secure elements'],
           'answer': 'poor performance on underrepresented groups'},
          {'question': 'Paragraph D suggests courts apply proportionality to',
           'options': ['only healthcare',
                       'limiting biometric dragnet searches',
                       'banning audit logs',
                       'requiring retail analytics'],
           'answer': 'limiting biometric dragnet searches'},
          {'question': "Paragraph F says children's templates may invalidate as traits",
           'options': ['evolve during growth',
                       'remain fixed forever',
                       'eliminate consent rules',
                       'ban travel retention'],
           'answer': 'evolve during growth'},
          {'question': 'The final paragraph argues bodies',
           'options': ['are renewable passwords',
                       'are not passwords and need governance',
                       'should replace all possession factors',
                       'require no policy literacy'],
           'answer': 'are not passwords and need governance'}],
  'short_answer': [{'question': 'What attacks try to fool sensors with masks?',
                    'answer': 'presentation',
                    'word_limit': 1},
                   {'question': 'What vein pattern scanners reduce contact infections?',
                    'answer': 'palm-vein',
                    'word_limit': 2},
                   {'question': 'What logs must track record access in healthcare?',
                    'answer': 'audit',
                    'word_limit': 1},
                   {'question': 'What detection resists synthetic media in future standards?',
                    'answer': 'liveness',
                    'word_limit': 1}]},
 {'quiz_number': 19,
  'title': 'Educational technology platforms',
  'topic_category': 'Education',
  'paragraphs': {'A': 'Educational technology platforms deliver learning management, video '
                      'conferencing, and adaptive exercises scaling instruction beyond physical '
                      'classroom walls. Institutions accelerated adoption during public health '
                      'emergencies, revealing gaps in home connectivity and device access among '
                      'economically disadvantaged students. Pedagogical research cautions that '
                      'digitisation without instructional design may replicate lecture '
                      'inefficiencies in clickable formats offering illusion of interactivity. '
                      'Privacy regulations govern student data collected by analytics tracking '
                      'clickstreams, webcam proctoring, and discussion forum participation. '
                      'Teachers require professional development interpreting dashboards without '
                      'reducing learners to reducible performance metrics alone. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'B': 'Adaptive engines recommend practice items based on item response theory '
                      'models estimating latent skill mastery probabilities. Over-reliance on '
                      'algorithmic pathways may narrow curricula toward easily autograded '
                      'objectives neglecting collaborative projects and creative writing. Open '
                      'educational resources reduce licensing costs, yet quality control and '
                      'localisation labour remain necessary for culturally relevant materials. The '
                      'author advocates blending teacher judgment with adaptive hints rather than '
                      'fully automated pacing removing human encouragement. Transparency about '
                      'recommendation logic helps families understand why particular remediation '
                      'appears for their children. Cross-disciplinary collaboration, sustained '
                      'funding, and careful communication with affected communities remain central '
                      'to credible long-term outcomes.',
                 'C': 'Accessibility standards mandate captions, keyboard navigation, and screen '
                      'reader compatibility so disabilities do not exclude participation. Vendors '
                      'claim compliance while automated scanners miss nuanced barriers in complex '
                      'interactive simulations used for science labs. Disability advocates '
                      'participate in procurement evaluations demanding real-user testing beyond '
                      'checkbox certification documents. Procurement contracts should include '
                      'remediation timelines when audits discover violations after deployment '
                      'semesters begin. The writer believes inclusive design benefits all '
                      'learners, not only those formally registered with disability services '
                      'offices. Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes. Policymakers increasingly demand reproducible evidence, '
                      'open data, and independent evaluation before scaling interventions beyond '
                      'controlled pilot settings.',
                 'D': 'Learning analytics dashboards visualise engagement heatmaps prompting '
                      'instructors to reach out students disappearing after midterm assessments. '
                      'Ethical guidelines caution against punitive uses treating login counts as '
                      'proxies for effort ignoring caregiving responsibilities at home. Predictive '
                      'dropout models risk labelling students self-fulfilling prophecies unless '
                      'interventions provide genuine support resources. Student unions request '
                      'opt-out options for non-essential analytics while preserving grades and '
                      'attendance records legally required. The author contends analytics should '
                      'empower supportive coaching cultures instead of surveillance disciplining '
                      'already stressed adolescents. Cross-disciplinary collaboration, sustained '
                      'funding, and careful communication with affected communities remain central '
                      'to credible long-term outcomes.',
                 'E': 'Commercial platform consolidation concentrates market power among few '
                      'suppliers integrating email, grades, and identity single sign-on. Vendor '
                      'lock-in complicates migration when institutions discover unfavourable '
                      'contract clauses or declining service quality mid-license. Interoperability '
                      'standards like common cartridge formats aim to let content move between '
                      'systems without costly reauthoring. Federated identity partnerships must '
                      'protect minors from advertising trackers embedded in supposedly educational '
                      'skins. The writer urges public sector bargaining leveraging collective '
                      'purchasing for privacy and portability guarantees. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes. Policymakers '
                      'increasingly demand reproducible evidence, open data, and independent '
                      'evaluation before scaling interventions beyond controlled pilot settings.',
                 'F': 'Teacher communities share remixable lesson sequences on open repositories, '
                      'building professional networks transcending isolated classroom '
                      'experimentation. Moderation policies must address inappropriate uploads '
                      'while preserving educator autonomy to discuss controversial historical '
                      'topics responsibly. Credentialing programmes recognise digital '
                      'instructional design skills alongside subject matter expertise in hiring '
                      'rubrics. Rural schools benefit disproportionately from synchronous virtual '
                      'field trips connecting students to museum educators globally. The author '
                      'sees technology amplifying excellent teaching but unable to substitute '
                      'underfunded staffing ratios permanently. Cross-disciplinary collaboration, '
                      'sustained funding, and careful communication with affected communities '
                      'remain central to credible long-term outcomes. Policymakers increasingly '
                      'demand reproducible evidence, open data, and independent evaluation before '
                      'scaling interventions beyond controlled pilot settings.',
                 'G': 'Future classrooms may blend embodied projects with augmented overlays '
                      'visualising molecular structures manipulable in three dimensions. Equity '
                      'audits should track whether new tools widen or close achievement gaps '
                      'across socioeconomic and language groups. The writer expects sustainable '
                      'edtech policy to centre learner wellbeing, data dignity, and teacher '
                      'professionalism jointly. Longitudinal studies must evaluate outcomes beyond '
                      'short-term test bumps following novelty effects of shiny interfaces. '
                      'Educational technology ultimately succeeds when it democratises opportunity '
                      'without commodifying childhood attention for unrelated commercial ends. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.'},
  'tfng': [{'question': 'Adaptive systems use item response theory models.', 'answer': 'True'},
           {'question': 'All vendors pass real-user accessibility testing automatically.',
            'answer': 'False'},
           {'question': 'Every institution migrated platforms easily without lock-in issues.',
            'answer': 'Not Given'},
           {'question': 'Predictive dropout models can become self-fulfilling without support.',
            'answer': 'True'},
           {'question': 'The passage claims technology alone fixes understaffing permanently.',
            'answer': 'False'}],
  'ynng': [{'question': 'The author wants analytics used for supportive coaching not punitive '
                        'surveillance.',
            'answer': 'Yes'},
           {'question': 'The writer believes automated pacing should remove teacher encouragement.',
            'answer': 'No'},
           {'question': 'The author supports collective bargaining for privacy guarantees.',
            'answer': 'Yes'},
           {'question': 'The writer thinks inclusive design helps only registered disability '
                        'offices.',
            'answer': 'No'},
           {'question': 'The author prioritises learner wellbeing and data dignity together.',
            'answer': 'Yes'}],
  'matching_headings': [{'paragraph': 'B',
                         'correct': 'ii. Adaptive engines and curriculum narrowing'},
                        {'paragraph': 'C',
                         'correct': 'iii. Accessibility audits and real-user testing'},
                        {'paragraph': 'D', 'correct': 'iv. Dropout prediction and opt-out rights'},
                        {'paragraph': 'E',
                         'correct': 'v. Vendor lock-in and interoperability standards'},
                        {'paragraph': 'F',
                         'correct': 'vi. Open repositories and rural virtual trips'}],
  'headings_pool': ['i. Baroque violin string monopolies',
                    'j. Adaptive engines and curriculum narrowing',
                    'k. Accessibility audits and real-user testing',
                    'l. Dropout prediction and opt-out rights',
                    'm. Vendor lock-in and interoperability standards',
                    'n. Open repositories and rural virtual trips',
                    'o. Ancient lighthouse fuel ratios'],
  'matching_info': [{'question': 'mention of item response theory mastery estimates',
                     'paragraph': 'B'},
                    {'question': 'reference to disability advocates in procurement',
                     'paragraph': 'C'},
                    {'question': 'discussion of opt-out for non-essential analytics',
                     'paragraph': 'D'},
                    {'question': 'examples of common cartridge interoperability formats',
                     'paragraph': 'E'},
                    {'question': 'a conclusion about democratising opportunity without '
                                 'commodifying attention',
                     'paragraph': 'G'}],
  'sentence_completion': [{'question': 'Webcam proctoring collects sensitive student ____.',
                           'answer': 'data'},
                          {'question': 'Open resources still need quality control and ____.',
                           'answer': 'localisation'},
                          {'question': 'Heatmaps may prompt outreach after midterm ____.',
                           'answer': 'assessments'},
                          {'question': 'Augmented overlays may visualise molecular ____.',
                           'answer': 'structures'}],
  'summary_completion': [{'question': 'Public health emergencies revealed home connectivity ____.',
                          'answer': 'gaps'},
                         {'question': 'Automated scanners may miss barriers in interactive ____.',
                          'answer': 'simulations'},
                         {'question': 'Federated identity must block advertising ____.',
                          'answer': 'trackers'},
                         {'question': 'Longitudinal studies should look beyond novelty ____ '
                                      'effects.',
                          'answer': 'effects'}],
  'table_completion': [{'question': 'Pedagogy risk | Digitisation may replicate inefficient ____',
                        'answer': 'lectures'},
                       {'question': 'Ethics | Login counts are poor proxies for ____',
                        'answer': 'effort'},
                       {'question': 'Market | Consolidation integrates grades and identity '
                                    'sign-____',
                        'answer': 'on'}],
  'mcq': [{'question': 'Paragraph A warns digitisation without design may create',
           'options': ['genuine interactivity automatically',
                       'illusion of interactivity in clickable lectures',
                       'no privacy issues',
                       'mandatory proctoring bans'],
           'answer': 'illusion of interactivity in clickable lectures'},
          {'question': 'According to paragraph B, adaptive engines may neglect',
           'options': ['autograded items',
                       'collaborative projects and creative writing',
                       'teacher judgment entirely by law',
                       'open resources'],
           'answer': 'collaborative projects and creative writing'},
          {'question': 'Paragraph D suggests analytics should avoid',
           'options': ['supportive coaching',
                       'punitive surveillance treating logins as effort',
                       'grade records',
                       'outreach'],
           'answer': 'punitive surveillance treating logins as effort'},
          {'question': 'Paragraph E promotes standards helping content',
           'options': ['move between systems',
                       'stay locked forever',
                       'embed trackers',
                       'eliminate teachers'],
           'answer': 'move between systems'},
          {'question': 'The final paragraph measures success by',
           'options': ['commodifying childhood attention',
                       'democratising opportunity responsibly',
                       'short-term test bumps only',
                       'ending embodied projects'],
           'answer': 'democratising opportunity responsibly'}],
  'short_answer': [{'question': 'What theory underlies adaptive mastery estimates?',
                    'answer': 'item response',
                    'word_limit': 2},
                   {'question': 'What standards require captions and keyboard navigation?',
                    'answer': 'accessibility',
                    'word_limit': 1},
                   {'question': 'What policies let students decline non-essential tracking?',
                    'answer': 'opt-out',
                    'word_limit': 1},
                   {'question': 'What trips connect rural schools to museums virtually?',
                    'answer': 'field trips',
                    'word_limit': 2}]},
 {'quiz_number': 20,
  'title': 'Quantum key distribution',
  'topic_category': 'Technology',
  'paragraphs': {'A': 'Quantum key distribution exchanges cryptographic keys encoded in quantum '
                      'states of photons such that eavesdropping introduces detectable '
                      'disturbances alerting communicating parties. Unlike mathematical public-key '
                      'schemes vulnerable to future quantum computers, information-theoretic '
                      'security of properly implemented quantum key distribution relies on physics '
                      'rather than computational hardness assumptions. Fiber networks between '
                      'financial centres and government campuses host early commercial links, '
                      'while satellite demonstrations extend reach toward global coverage '
                      'aspirations. Engineering challenges include photon loss over distance, '
                      'detector dark counts, and synchronising clocks across metropolitan-scale '
                      'deployments. Pilots justify costs for ultra-sensitive traffic, not yet for '
                      'every consumer messaging application.',
                 'B': 'Prepare-and-measure protocols send polarised or phase-encoded pulses, while '
                      'entanglement-based schemes distribute correlated pairs measured '
                      'independently at distant stations. Error correction and privacy '
                      'amplification distil raw key material into strings satisfying randomness '
                      'tests despite channel noise. Side-channel attacks target implementation '
                      'flaws in detectors or lasers rather than breaking fundamental quantum '
                      'principles. Certification laboratories evaluate modules against common '
                      'criteria derived from theoretical security proofs adapted to finite-size '
                      'effects. The author stresses that security claims require scrutiny of '
                      'entire systems, not laboratory idealisations ignoring engineering '
                      'realities. Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'C': 'Integration with existing public-key infrastructure uses quantum-derived '
                      'keys to seed symmetric algorithms protecting bulk data efficiently. Hybrid '
                      'architectures maintain classical authentication while upgrading '
                      'confidentiality layers, acknowledging that initial authentication may still '
                      'need post-quantum signatures. Network operators debate whether dedicated '
                      'dark fibers are necessary or whether quantum signals can coexist with '
                      'classical channels using wavelength division. Cost models include '
                      'maintenance of cryogenic or cooled detectors depending on technology '
                      'choices. The writer believes phased deployment starting with backbone links '
                      'balances expense against harvest-now-decrypt-later risks. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'D': 'National programmes fund metropolitan testbeds linking research '
                      'universities with supercomputing centres handling export-controlled '
                      'simulations. Export controls restrict sale of high-performance '
                      'single-photon sources to certain jurisdictions, shaping geopolitical supply '
                      'chains. Standards bodies publish interface specifications so vendors build '
                      'interoperable equipment rather than incompatible national silos. '
                      'Procurement officers request transparency on mean time between failures '
                      'affecting service availability commitments. The author contends '
                      'international cooperation accelerates maturity more than secretive '
                      'duplication of incompatible prototypes. Cross-disciplinary collaboration, '
                      'sustained funding, and careful communication with affected communities '
                      'remain central to credible long-term outcomes. Policymakers increasingly '
                      'demand reproducible evidence, open data, and independent evaluation before '
                      'scaling interventions beyond controlled pilot settings.',
                 'E': 'Free-space links bridge rivers or connect buildings where trenching fiber '
                      'is prohibitively expensive, vulnerable to weather and alignment drift. '
                      'Adaptive optics correct turbulence for ground-to-satellite channels '
                      'relaying keys to remote ground stations. Daylight operation remains '
                      'difficult because background photons overwhelm weak quantum signals without '
                      'narrow filtering. Mobile platforms on aircraft or ships experiment with '
                      'stabilised terminals, though operational readiness lags fixed '
                      'installations. The writer cautions that atmospheric variability demands '
                      'conservative security margins in key rate calculations. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes. Policymakers '
                      'increasingly demand reproducible evidence, open data, and independent '
                      'evaluation before scaling interventions beyond controlled pilot settings.',
                 'F': 'Regulators examine whether quantum-secured networks require new liability '
                      'frameworks when outages delay trading settlements. Insurance products '
                      'emerge covering business interruption from key distribution failures '
                      'distinct from classical cyber policies. Auditors verify chain-of-custody '
                      'for hardware modules preventing substitution of compromised devices during '
                      'logistics. Ethical debates consider equal access to quantum-safe '
                      'communications for civil society groups in authoritarian contexts. The '
                      'author supports dual-use governance preventing surveillance monopolies '
                      'while enabling defensive upgrades for critical infrastructure. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes. Policymakers increasingly demand reproducible evidence, '
                      'open data, and independent evaluation before scaling interventions beyond '
                      'controlled pilot settings.',
                 'G': 'Future terrestrial networks may mesh quantum repeaters extending distances '
                      'beyond current trusted-node chains splitting keys hop by hop. Repeaters '
                      'remain experimental, so near-term architecture relies on carefully secured '
                      'intermediate stations monitored continuously. The writer expects quantum '
                      'key distribution to complement, not replace, broader post-quantum '
                      'cryptography migration programmes. Education initiatives helping engineers '
                      'interpret security proofs will reduce misconfigured deployments undermining '
                      'theoretical guarantees. When integrated thoughtfully, quantum key '
                      'distribution strengthens trust anchors for the quantum era without magical '
                      'thinking. Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes. Policymakers increasingly demand reproducible evidence, '
                      'open data, and independent evaluation before scaling interventions beyond '
                      'controlled pilot settings.'},
  'tfng': [{'question': 'Eavesdropping on quantum keys can introduce detectable disturbances.',
            'answer': 'True'},
           {'question': 'Quantum key distribution secures all authentication without classical '
                        'methods.',
            'answer': 'False'},
           {'question': 'Every consumer chat app uses commercial quantum links today.',
            'answer': 'Not Given'},
           {'question': 'Side-channel attacks exploit implementation flaws in detectors.',
            'answer': 'True'},
           {'question': 'Repeaters are already widely deployed in production networks.',
            'answer': 'False'}],
  'ynng': [{'question': 'The author wants scrutiny of entire engineered systems not ideals alone.',
            'answer': 'Yes'},
           {'question': 'The writer believes quantum keys should instantly replace all '
                        'post-quantum work.',
            'answer': 'No'},
           {'question': 'The author supports cooperative standards over incompatible national '
                        'silos.',
            'answer': 'Yes'},
           {'question': 'The writer dismisses atmospheric effects on free-space security margins.',
            'answer': 'No'},
           {'question': 'The author favours dual-use governance preventing surveillance '
                        'monopolies.',
            'answer': 'Yes'}],
  'matching_headings': [{'paragraph': 'B',
                         'correct': 'ii. Protocol types and privacy amplification'},
                        {'paragraph': 'C',
                         'correct': 'iii. Hybrid integration with classical infrastructure'},
                        {'paragraph': 'D',
                         'correct': 'iv. Testbeds, export controls, and standards'},
                        {'paragraph': 'E',
                         'correct': 'v. Free-space, satellite, and atmospheric limits'},
                        {'paragraph': 'F',
                         'correct': 'vi. Liability, insurance, and dual-use ethics'}],
  'headings_pool': ['i. Medieval parchment tariff schedules',
                    'j. Protocol types and privacy amplification',
                    'k. Hybrid integration with classical infrastructure',
                    'l. Testbeds, export controls, and standards',
                    'm. Free-space, satellite, and atmospheric limits',
                    'n. Liability, insurance, and dual-use ethics',
                    'o. Victorian steamship coal ratios'],
  'matching_info': [{'question': 'explanation of privacy amplification distilling raw keys',
                     'paragraph': 'B'},
                    {'question': 'discussion of hybrid classical authentication with quantum '
                                 'confidentiality',
                     'paragraph': 'C'},
                    {'question': 'reference to export controls on photon sources',
                     'paragraph': 'D'},
                    {'question': 'mention of adaptive optics for satellite channels',
                     'paragraph': 'E'},
                    {'question': 'a balanced view complementing post-quantum cryptography '
                                 'programmes',
                     'paragraph': 'G'}],
  'sentence_completion': [{'question': 'Photon loss and detector dark counts limit practical ____.',
                           'answer': 'distance'},
                          {'question': 'Privacy amplification produces strings passing randomness '
                                       '____.',
                           'answer': 'tests'},
                          {'question': 'Wavelength division may let quantum signals coexist with '
                                       '____ channels.',
                           'answer': 'classical'},
                          {'question': 'Trusted-node chains split keys hop by ____ until repeaters '
                                       'mature.',
                           'answer': 'hop'}],
  'summary_completion': [{'question': 'Information-theoretic security relies on physics not '
                                      'computational ____ assumptions.',
                          'answer': 'hardness'},
                         {'question': 'Certification adapts proofs to finite-size ____ effects.',
                          'answer': 'size'},
                         {'question': 'Free-space links suffer alignment drift and ____ '
                                      'turbulence.',
                          'answer': 'atmospheric'},
                         {'question': 'Auditors verify hardware chain-of-____ during logistics.',
                          'answer': 'custody'}],
  'table_completion': [{'question': 'Channel issue | Error correction handles quantum ____',
                        'answer': 'noise'},
                       {'question': 'Deployment | Phased backbone rollout addresses '
                                    'harvest-now-decrypt-____ risks',
                        'answer': 'later'},
                       {'question': 'Education | Engineers must interpret security ____ to avoid '
                                    'misconfiguration',
                        'answer': 'proofs'}],
  'mcq': [{'question': 'Paragraph A positions quantum key distribution for',
           'options': ['every consumer app',
                       'ultra-sensitive traffic on fiber links',
                       'replacing all symmetric crypto',
                       'eliminating detectors'],
           'answer': 'ultra-sensitive traffic on fiber links'},
          {'question': 'According to paragraph B, finite-size effects influence',
           'options': ['only classical keys',
                       'certification of real modules',
                       'ban on entanglement',
                       'satellite bans'],
           'answer': 'certification of real modules'},
          {'question': 'Paragraph E notes daylight free-space is hard because',
           'options': ['background photons overwhelm signals',
                       'fiber is illegal',
                       'repeaters are mandatory',
                       'optics cannot adapt'],
           'answer': 'background photons overwhelm signals'},
          {'question': 'Paragraph F introduces insurance for interruptions from',
           'options': ['key distribution failures',
                       'classical phishing only',
                       'parchment tariffs',
                       'steamship coal'],
           'answer': 'key distribution failures'},
          {'question': 'The final paragraph expects quantum keys to',
           'options': ['replace all migration efforts',
                       'complement post-quantum cryptography programmes',
                       'end education initiatives',
                       'require magical thinking'],
           'answer': 'complement post-quantum cryptography programmes'}],
  'short_answer': [{'question': 'What particles often encode quantum keys?',
                    'answer': 'photons',
                    'word_limit': 1},
                   {'question': 'What attacks target flawed detectors rather than physics?',
                    'answer': 'side-channel',
                    'word_limit': 1},
                   {'question': 'What optics correct turbulence for satellite links?',
                    'answer': 'adaptive',
                    'word_limit': 1},
                   {'question': 'What experimental devices could extend distance beyond trusted '
                                'nodes?',
                    'answer': 'repeaters',
                    'word_limit': 1}]},
 {'quiz_number': 21,
  'title': 'Tropical reforestation economics',
  'topic_category': 'Environment',
  'paragraphs': {'A': 'Tropical reforestation projects aim to restore degraded forests, sequester '
                      'carbon, and support biodiversity while generating livelihoods for rural '
                      'communities long excluded from formal markets. Carbon credit markets '
                      'finance plantings when verifiers certify additional biomass accumulation '
                      'beyond baseline deforestation trends documented historically. Native '
                      'species mixtures cost more initially than monoculture timber plantations '
                      'yet deliver superior habitat connectivity and resilience to pests. Land '
                      'tenure clarity determines whether communities benefit or lose access when '
                      'investors fence newly registered concessions. Economists model opportunity '
                      'costs of alternative land uses including subsistence agriculture, cattle '
                      'ranching, and illicit crop cultivation. Cross-disciplinary collaboration, '
                      'sustained funding, and careful communication with affected communities '
                      'remain central to credible long-term outcomes.',
                 'B': 'Payment for ecosystem services schemes transfer funds to stewards '
                      'maintaining forest cover, sometimes using satellite monitoring to detect '
                      'unauthorised clearing. Leakage occurs if displaced cattle ranching simply '
                      'moves to neighboring uncleared plots, negating net climate benefits unless '
                      'regional planning coordinates incentives. Buffer zones around protected '
                      'areas employ community patrols combining indigenous knowledge with drone '
                      'overflights documenting incursions. The author insists contracts include '
                      'grievance mechanisms and revenue sharing rather than top-down conservation '
                      'excluding traditional users. Without enforcement budgets, signed agreements '
                      'decay into paper parks vulnerable to illegal logging during commodity price '
                      'spikes. Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'C': 'Nursery capacity limits scale-up when seed collection, genetic diversity, '
                      'and mycorrhizal inoculation require skilled technicians year-round. '
                      'Seasonal planting windows align with rainfall patterns; mistiming increases '
                      'mortality wasting upfront investments in seedlings and transport logistics. '
                      'Mixed-species designs need longer validation before carbon methodologies '
                      'accept allometric growth equations traditionally calibrated on teak '
                      'plantations. Researchers deploy terrestrial laser scanning to measure '
                      'biomass accurately, reducing disputes between auditors and project '
                      'developers. The writer supports methodological innovation preventing '
                      'perverse incentives to plant fast-growing exotic species unsuitable for '
                      'local fauna. Cross-disciplinary collaboration, sustained funding, and '
                      'careful communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'D': 'Microfinance and cooperative ownership models let smallholders aggregate '
                      'parcels meeting minimum project sizes attractive to international buyers. '
                      'Gender-inclusive governance ensures women participate in decision-making '
                      'about land use affecting fuelwood collection and water fetching routes. '
                      'Corruption risks inflate planted hectare claims unless independent '
                      'verification samples plots with geographic randomisation. Whistleblower '
                      'protections encourage reporting falsified survival rates after droughts '
                      'kill vulnerable saplings quietly. The author contends integrity systems '
                      'cost less than reputational collapse when investigative journalists expose '
                      'fraudulent credits. Cross-disciplinary collaboration, sustained funding, '
                      'and careful communication with affected communities remain central to '
                      'credible long-term outcomes. Policymakers increasingly demand reproducible '
                      'evidence, open data, and independent evaluation before scaling '
                      'interventions beyond controlled pilot settings.',
                 'E': 'Biodiversity co-benefits attract philanthropic grants supplementing carbon '
                      'revenue, funding camera traps monitoring apex predators returning to '
                      'corridors. Ecotourism ventures create jobs as guides interpreting restored '
                      'forests, though pandemic shocks demonstrated vulnerability to tourism '
                      'dependence. Agroforestry integrates shade-grown crops under canopy, '
                      'blending food security with partial canopy cover satisfying crediting '
                      'rules. Nutrition programmes link school meals to orchard plantings teaching '
                      'students horticultural skills alongside environmental stewardship. The '
                      'writer believes diversified income streams stabilise communities against '
                      'carbon price volatility on voluntary markets. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes.',
                 'F': 'National REDD-plus frameworks align local projects with emissions '
                      'accounting in nationally determined contributions submitted to climate '
                      'treaties. Double counting arises if both project developers and national '
                      'inventories claim identical tonnes without corresponding adjustments. Legal '
                      'scholars debate whether sovereign carbon registries supersede private '
                      'certifications when conflicts emerge during compliance periods. Capacity '
                      'building trains government foresters in geographic information systems '
                      'improving transparency for civil society watchdogs. The author urges nested '
                      'accounting rules resolving overlaps before marketing credits to '
                      'multinational corporations. Cross-disciplinary collaboration, sustained '
                      'funding, and careful communication with affected communities remain central '
                      'to credible long-term outcomes. Cross-disciplinary collaboration, sustained '
                      'funding, and careful communication with affected communities remain central '
                      'to credible long-term outcomes.',
                 'G': 'Long-term success requires fire management, invasive species control, and '
                      'adaptive grazing agreements with neighbours maintaining connectivity. '
                      'Climate change may shift suitable ranges faster than restoration timelines, '
                      'forcing assisted migration of heat-sensitive seed sources. The writer '
                      'foresees reforestation economics maturing when integrity, tenure justice, '
                      'and ecological science receive equal billing in contracts. Investors should '
                      'accept modest returns reflecting genuine risk rather than expecting quick '
                      'profits from unverified paper trees. Restored tropical forests can '
                      'simultaneously store carbon, regulate water, and affirm community rights '
                      'when economics serves ecology rather than reversing priorities. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.'},
  'tfng': [{'question': 'Native mixtures often outperform monocultures for habitat connectivity.',
            'answer': 'True'},
           {'question': 'Leakage is impossible if one project fences its plot.', 'answer': 'False'},
           {'question': 'All reforestation projects include decade-long verified survival data in '
                        'the passage.',
            'answer': 'Not Given'},
           {'question': 'Terrestrial laser scanning can improve biomass measurement.',
            'answer': 'True'},
           {'question': 'The passage states carbon prices never fluctuate on voluntary markets.',
            'answer': 'False'}],
  'ynng': [{'question': 'The author demands grievance mechanisms and revenue sharing in contracts.',
            'answer': 'Yes'},
           {'question': 'The writer supports exotic fast-growing species regardless of fauna '
                        'needs.',
            'answer': 'No'},
           {'question': 'The author believes integrity systems prevent costly reputational '
                        'collapse.',
            'answer': 'Yes'},
           {'question': 'The writer thinks double counting concerns are irrelevant to REDD-plus.',
            'answer': 'No'},
           {'question': 'The author wants ecology and tenure justice equal to carbon accounting.',
            'answer': 'Yes'}],
  'matching_headings': [{'paragraph': 'B',
                         'correct': 'ii. Payments, leakage, and community patrols'},
                        {'paragraph': 'C',
                         'correct': 'iii. Nursery limits and laser scanning biomass'},
                        {'paragraph': 'D',
                         'correct': 'iv. Cooperatives, gender governance, and corruption'},
                        {'paragraph': 'E',
                         'correct': 'v. Ecotourism, agroforestry, and diversified incomes'},
                        {'paragraph': 'F', 'correct': 'vi. REDD-plus nesting and double counting'}],
  'headings_pool': ['i. Baroque clockspring import duties',
                    'j. Payments, leakage, and community patrols',
                    'k. Nursery limits and laser scanning biomass',
                    'l. Cooperatives, gender governance, and corruption',
                    'm. Ecotourism, agroforestry, and diversified incomes',
                    'n. REDD-plus nesting and double counting',
                    'o. Ancient bronze ingot trade'],
  'matching_info': [{'question': 'discussion of leakage from displaced cattle ranching',
                     'paragraph': 'B'},
                    {'question': 'reference to mycorrhizal inoculation and seasonal windows',
                     'paragraph': 'C'},
                    {'question': 'mention of geographic randomisation verifying planted hectares',
                     'paragraph': 'D'},
                    {'question': 'examples of shade-grown agroforestry crops', 'paragraph': 'E'},
                    {'question': 'a conclusion balancing carbon, water, and community rights',
                     'paragraph': 'G'}],
  'sentence_completion': [{'question': 'Carbon finance requires verifiers certifying additional '
                                       'biomass ____.',
                           'answer': 'accumulation'},
                          {'question': 'Buffer zones may combine indigenous knowledge with drone '
                                       '____.',
                           'answer': 'overflights'},
                          {'question': 'Microfinance helps smallholders aggregate ____.',
                           'answer': 'parcels'},
                          {'question': 'Nested accounting prevents overlaps between national and '
                                       'private ____.',
                           'answer': 'claims'}],
  'summary_completion': [{'question': 'Opportunity costs include subsistence agriculture and '
                                      'cattle ____.',
                          'answer': 'ranching'},
                         {'question': 'Independent sampling counters inflated hectare ____.',
                          'answer': 'claims'},
                         {'question': 'Philanthropic grants may fund camera ____ monitoring '
                                      'predators.',
                          'answer': 'traps'},
                         {'question': 'Assisted migration may move heat-sensitive seed ____.',
                          'answer': 'sources'}],
  'table_completion': [{'question': 'Tenure issue | Unclear land rights may exclude traditional '
                                    '____',
                        'answer': 'users'},
                       {'question': 'Integrity | Fraud exposure rises without whistleblower ____',
                        'answer': 'protections'},
                       {'question': 'Climate risk | Ranges may shift faster than restoration ____',
                        'answer': 'timelines'}],
  'mcq': [{'question': 'Paragraph A says native mixtures offer',
           'options': ['cheaper short-term monoculture only',
                       'superior habitat connectivity',
                       'no tenure concerns',
                       'guaranteed illicit crop profits'],
           'answer': 'superior habitat connectivity'},
          {'question': 'According to paragraph B, paper parks fail without',
           'options': ['enforcement budgets',
                       'more cattle leakage',
                       'banning drones',
                       'ending grievance mechanisms'],
           'answer': 'enforcement budgets'},
          {'question': 'Paragraph D promotes gender-inclusive',
           'options': ['decision-making on land use',
                       'elimination of all microfinance',
                       'randomised corruption',
                       'exclusive male governance'],
           'answer': 'decision-making on land use'},
          {'question': 'Paragraph F warns double counting if',
           'options': ['both projects and nations claim same tonnes',
                       'only satellites are used',
                       'agroforestry is banned',
                       'ecotourism collapses'],
           'answer': 'both projects and nations claim same tonnes'},
          {'question': 'The final paragraph says economics should serve',
           'options': ['ecology with community rights',
                       'quick unverified profits only',
                       'paper trees',
                       'ignoring fire management'],
           'answer': 'ecology with community rights'}],
  'short_answer': [{'question': 'What finance mechanism pays stewards maintaining forest cover?',
                    'answer': 'ecosystem services',
                    'word_limit': 2},
                   {'question': 'What scanning technology measures biomass accurately?',
                    'answer': 'laser',
                    'word_limit': 1},
                   {'question': 'What framework aligns projects with national climate '
                                'contributions?',
                    'answer': 'REDD-plus',
                    'word_limit': 1},
                   {'question': 'What income blends crops under restored canopy?',
                    'answer': 'agroforestry',
                    'word_limit': 1}]},
 {'quiz_number': 22,
  'title': 'Coral reef restoration',
  'topic_category': 'Environment',
  'paragraphs': {'A': 'Coral reef restoration responds to mass bleaching, storm damage, and '
                      'chronic pollution degrading carbonate structures supporting fisheries and '
                      'coastal protection worldwide. Practitioners propagate fragments in '
                      'underwater nurseries before outplanting onto degraded substrates using '
                      'cement bases or modular frames. Heat-tolerant genotypes identified through '
                      'stress experiments offer hope, yet moving corals across regions raises '
                      'genetic homogenisation and disease transfer risks. Restoration budgets '
                      'rarely match scale of decline, forcing triage prioritising reefs protecting '
                      'dense human settlements and culturally sacred sites. Monitoring requires '
                      'multi-year commitments tracking survival, predation, and recruitment rather '
                      'than celebrating one-off planting photo opportunities. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes.',
                 'B': 'Coral gardening teams clean algae competition and remove coralivorous '
                      'snails threatening fragile transplants during early establishment months. '
                      'Microfragmentation accelerates growth by cutting colonies into tiny pieces '
                      'that fuse into larger structures over surprisingly short intervals in '
                      'optimal conditions. 3D-printed artificial reefs provide settlement surfaces '
                      'mimicking complex topography when natural rubble lacks stable anchorage for '
                      'new colonies. The author cautions that artificial structures cannot replace '
                      'ecological functions of mature reef mosaics built over centuries of '
                      'biogenic accretion. Engineering solutions must complement watershed '
                      'management reducing sediment runoff that smothers corals after heavy rains. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'C': 'Broodstock banks preserve gametes and larvae from spawning synchronisation '
                      'events occurring on predictable lunar cycles. Larval seeding disperses '
                      'cultured offspring across reefs using mesh enclosures, attempting to boost '
                      'natural recruitment suppressed by degraded water quality. Legal permits '
                      'govern collection of wild broodstock to avoid depleting remaining healthy '
                      'populations already stressed by warming seas. Indigenous custodians '
                      'increasingly co-manage projects integrating traditional seasonal closures '
                      'with scientific spawning calendars. The writer believes co-governance '
                      'improves compliance compared with externally imposed interventions ignoring '
                      'local marine tenure. Cross-disciplinary collaboration, sustained funding, '
                      'and careful communication with affected communities remain central to '
                      'credible long-term outcomes.',
                 'D': 'Water quality interventions upgrade wastewater treatment and agricultural '
                      'buffers upstream, addressing root drivers of reef decline. Nutrient '
                      'enrichment fuels macroalgae blooms competing with coral recruits, while '
                      'sunscreens and pharmaceuticals appear in coastal waters at concerning '
                      'concentrations. Municipal infrastructure financing competes with visible '
                      'in-water planting favoured by politicians seeking rapid constituency '
                      'visibility. The author argues upstream investment yields larger sustained '
                      'benefits than cosmetic outplanting alone in chronically polluted bays. '
                      'Integrated coastal management links reef projects to mangrove '
                      'rehabilitation stabilising sediments and nursery habitats for reef fish. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'E': 'Tourism operators fund restoration levies on dive permits, marketing trips '
                      'to volunteer nurseries appealing to environmentally conscious visitors. '
                      'Greenwashing accusations arise when hotels highlight small plantings while '
                      'expanding coastal armouring damaging adjacent habitats. Certification '
                      'programmes audit operator practices, though enforcement capacity remains '
                      'limited on remote archipelagos. Economic analyses compare reef tourism '
                      'revenue lost during bleaching against cost-effectiveness of proactive '
                      'restoration corridors. The writer supports transparent accounting showing '
                      'how levy funds translate into measurable coral cover gains over decade '
                      'horizons. Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'F': 'Climate adaptation planning acknowledges that some reefs may function as '
                      'temporary refugia cooler than surrounding waters during marine heatwaves. '
                      'Connectivity modelling identifies larval sources replenishing downstream '
                      'reefs after catastrophic mortality events. Marine protected networks '
                      'designed using connectivity data may outperform isolated restoration plots '
                      'lacking larval supply. Skeptics question whether resources should shift '
                      'entirely toward emissions mitigation rather than local restoration. The '
                      'author contends both global decarbonisation and local stewardship are '
                      'necessary, not mutually exclusive strategies. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes. Policymakers '
                      'increasingly demand reproducible evidence, open data, and independent '
                      'evaluation before scaling interventions beyond controlled pilot settings.',
                 'G': 'Emerging probiotics and algal symbiont manipulations remain experimental '
                      'with uncertain ecological side effects at ecosystem scales. Regulatory '
                      'frameworks lag behind private startups marketing miracle treatments before '
                      'peer review completes long-term trials. The writer expects restoration to '
                      'mature into a discipline with open data repositories sharing failure rates '
                      'alongside successes. Training local technicians creates durable employment '
                      'beyond short grant cycles dependent on foreign consultants. Healthy reefs '
                      'ultimately depend on societal choices reducing emissions while actively '
                      'repairing damage within scientifically informed limits. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes.'},
  'tfng': [{'question': 'Nurseries propagate coral fragments before outplanting.',
            'answer': 'True'},
           {'question': 'Artificial reefs fully replace centuries-old reef functions immediately.',
            'answer': 'False'},
           {'question': 'Every hotel restoration levy is rigorously audited globally.',
            'answer': 'Not Given'},
           {'question': 'Upstream nutrient reduction can support reef recovery.', 'answer': 'True'},
           {'question': 'The passage rejects all local restoration in favour of emissions cuts '
                        'only.',
            'answer': 'False'}],
  'ynng': [{'question': 'The author warns artificial structures cannot replace mature reef '
                        'mosaics.',
            'answer': 'Yes'},
           {'question': 'The writer believes co-governance improves compliance over imposed '
                        'projects.',
            'answer': 'Yes'},
           {'question': 'The author thinks upstream wastewater investment beats cosmetic planting '
                        'in polluted bays.',
            'answer': 'Yes'},
           {'question': 'The writer claims probiotics are proven safe at ecosystem scale.',
            'answer': 'No'},
           {'question': 'The author supports both decarbonisation and local stewardship.',
            'answer': 'Yes'}],
  'matching_headings': [{'paragraph': 'B',
                         'correct': 'ii. Gardening, microfragmentation, and 3D substrates'},
                        {'paragraph': 'C', 'correct': 'iii. Broodstock banks and co-governance'},
                        {'paragraph': 'D',
                         'correct': 'iv. Upstream pollution and integrated coastal management'},
                        {'paragraph': 'E', 'correct': 'v. Tourism levies and greenwashing risks'},
                        {'paragraph': 'F',
                         'correct': 'vi. Refugia, connectivity, and mitigation debate'}],
  'headings_pool': ['i. Medieval stained glass lead trade',
                    'j. Gardening, microfragmentation, and 3D substrates',
                    'k. Broodstock banks and co-governance',
                    'l. Upstream pollution and integrated coastal management',
                    'm. Tourism levies and greenwashing risks',
                    'n. Refugia, connectivity, and mitigation debate',
                    'o. Ancient Roman road milestones'],
  'matching_info': [{'question': 'mention of microfragmentation accelerating colony fusion',
                     'paragraph': 'B'},
                    {'question': 'reference to indigenous seasonal closures with spawning '
                                 'calendars',
                     'paragraph': 'C'},
                    {'question': 'discussion of wastewater upgrades reducing nutrient enrichment',
                     'paragraph': 'D'},
                    {'question': 'examples of restoration levies on dive permits',
                     'paragraph': 'E'},
                    {'question': 'a conclusion requiring emissions cuts and informed repair',
                     'paragraph': 'G'}],
  'sentence_completion': [{'question': 'Bleaching and storms damage carbonate ____ supporting '
                                       'fisheries.',
                           'answer': 'structures'},
                          {'question': 'Larval seeding uses mesh ____ on degraded reefs.',
                           'answer': 'enclosures'},
                          {'question': 'Connectivity modelling tracks larval ____ between reefs.',
                           'answer': 'sources'},
                          {'question': 'Open repositories should share failure ____ alongside '
                                       'successes.',
                           'answer': 'rates'}],
  'summary_completion': [{'question': 'Heat-tolerant genotypes raise disease transfer and genetic '
                                      '____ risks.',
                          'answer': 'homogenisation'},
                         {'question': 'Sediment runoff after rains can ____ corals.',
                          'answer': 'smother'},
                         {'question': 'Marine protected networks may outperform isolated '
                                      'restoration ____.',
                          'answer': 'plots'},
                         {'question': 'Regulatory frameworks lag behind startup ____ treatments.',
                          'answer': 'miracle'}],
  'table_completion': [{'question': 'Field work | Teams remove coralivorous ____ threatening '
                                    'transplants',
                        'answer': 'snails'},
                       {'question': 'Tourism | Greenwashing may hide coastal ____ expansion',
                        'answer': 'armouring'},
                       {'question': 'Climate | Some reefs act as temporary heatwave ____',
                        'answer': 'refugia'}],
  'mcq': [{'question': 'Paragraph A notes budgets rarely match',
           'options': ['tourist demand',
                       'scale of reef decline',
                       'nursery legality',
                       'lunar cycles'],
           'answer': 'scale of reef decline'},
          {'question': 'According to paragraph B, 3D structures cannot replace',
           'options': ['centuries of biogenic accretion',
                       'all watershed work',
                       'permits',
                       'spawning'],
           'answer': 'centuries of biogenic accretion'},
          {'question': 'Paragraph D argues politicians favour',
           'options': ['invisible upstream pipes over visible planting',
                       'only mangrove bans',
                       'ending tourism',
                       'probiotic mandates'],
           'answer': 'invisible upstream pipes over visible planting'},
          {'question': 'Paragraph F says protected networks help when designed with',
           'options': ['connectivity data',
                       'isolated plots without larvae',
                       'hotels only',
                       'miracle startups'],
           'answer': 'connectivity data'},
          {'question': 'The final paragraph depends on reducing emissions while',
           'options': ['repairing within scientific limits',
                       'ending all nurseries',
                       'ignoring local jobs',
                       'avoiding data sharing'],
           'answer': 'repairing within scientific limits'}],
  'short_answer': [{'question': 'What underwater facilities grow fragments before outplanting?',
                    'answer': 'nurseries',
                    'word_limit': 1},
                   {'question': 'What printing technology creates settlement surfaces?',
                    'answer': '3D-printed',
                    'word_limit': 1},
                   {'question': 'What closures integrate traditional and scientific calendars?',
                    'answer': 'seasonal',
                    'word_limit': 1},
                   {'question': 'What organisms in corals are manipulated experimentally?',
                    'answer': 'symbionts',
                    'word_limit': 1}]},
 {'quiz_number': 23,
  'title': 'Circular economy models',
  'topic_category': 'Environment',
  'paragraphs': {'A': 'Circular economy models redesign production and consumption to minimise '
                      'waste by keeping materials in use through reuse, repair, remanufacturing, '
                      'and recycling loops. Linear take-make-dispose patterns deplete virgin '
                      'resources and generate emissions from extraction, manufacturing, and '
                      'landfill methane. Business models shift toward product-as-a-service, where '
                      'manufacturers retain ownership maintaining equipment while customers pay '
                      'for functional outcomes. Policy instruments include extended producer '
                      'responsibility fees funding collection infrastructure and design standards '
                      'easing disassembly. Measuring circularity requires indicators beyond '
                      'recycling rates, capturing material circulation and lifetime extension '
                      'holistically. Cross-disciplinary collaboration, sustained funding, and '
                      'careful communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'B': 'Design for repair mandates modular components, accessible fasteners, and '
                      'published schematics enabling independent technicians to replace worn '
                      'parts. Manufacturers sometimes resist sharing spare parts information '
                      'protecting aftermarket revenue, conflicting with right-to-repair '
                      'legislation gaining momentum. Digital product passports document material '
                      'composition, aiding sorters directing streams toward appropriate recycling '
                      'pathways. The author argues legal frameworks must balance intellectual '
                      'property with environmental imperatives preventing premature obsolescence. '
                      'Without enforcement, voluntary corporate pledges recycle familiar marketing '
                      'language without changing supply chains substantively. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes. Policymakers '
                      'increasingly demand reproducible evidence, open data, and independent '
                      'evaluation before scaling interventions beyond controlled pilot settings.',
                 'C': 'Industrial symbiosis parks colocate firms exchanging by-products, turning '
                      "one plant's waste heat or CO2 into another's feedstock. Kalundborg-style "
                      'ecosystems inspire planners, though replication demands trust and '
                      'logistical coordination absent in fragmented estates. Small and medium '
                      'enterprises lack analysts identifying symbiosis opportunities, requiring '
                      'regional facilitators brokering matches. Transport emissions from moving '
                      'materials between partners must be included in net benefit calculations '
                      'avoiding green mirages. The writer supports public investment in '
                      'facilitation networks scaling symbiosis beyond iconic pioneer sites. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes. Policymakers increasingly demand reproducible evidence, '
                      'open data, and independent evaluation before scaling interventions beyond '
                      'controlled pilot settings.',
                 'D': 'Consumer behaviour remains pivotal when cheap disposable goods undermine '
                      'premium durable alternatives lacking marketing budgets. Repair cafes and '
                      'community tool libraries cultivate cultures of maintenance, yet time '
                      'poverty limits participation among overworked households. Deposit-return '
                      'schemes boost beverage container collection rates where convenient reverse '
                      'vending machines accompany grocery trips. Behavioural nudges alone fail '
                      'without price signals internalising environmental externalities through '
                      'taxes or fee schedules. The author contends cultural change complements '
                      'regulation rather than replacing sturdy market rules. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes. Policymakers '
                      'increasingly demand reproducible evidence, open data, and independent '
                      'evaluation before scaling interventions beyond controlled pilot settings.',
                 'E': 'Global trade complicates circularity when discarded electronics ship to '
                      'informal recyclers exposing workers to hazardous fractions. Basel '
                      'Convention amendments tighten transboundary movement of e-waste, pushing '
                      'wealthier nations to build domestic processing capacity. Urban mining '
                      'recovers critical metals from stockpiles reducing dependence on '
                      'geopolitically sensitive mining regions. Automated disassembly robotics '
                      'remain nascent, so manual preprocessing still dominates economics in many '
                      'facilities. The writer urges ethical sourcing standards covering secondary '
                      'materials as rigorously as virgin mines. Cross-disciplinary collaboration, '
                      'sustained funding, and careful communication with affected communities '
                      'remain central to credible long-term outcomes. Policymakers increasingly '
                      'demand reproducible evidence, open data, and independent evaluation before '
                      'scaling interventions beyond controlled pilot settings.',
                 'F': 'Financial institutions develop taxonomies classifying circular investments '
                      'eligible for green bonds, though greenwashing scrutiny intensifies '
                      'accordingly. Lifecycle assessments inform procurement rules for public '
                      'infrastructure selecting longer-lasting materials despite higher upfront '
                      'costs. Accountants debate how to depreciate assets designed for multiple '
                      'lifecycles across remanufacturing iterations. Insurance products may reward '
                      'modular buildings whose components can be reused after seismic events. The '
                      'author believes aligning accounting standards with circular metrics unlocks '
                      'capital otherwise favouring disposable models. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes. Policymakers '
                      'increasingly demand reproducible evidence, open data, and independent '
                      'evaluation before scaling interventions beyond controlled pilot settings.',
                 'G': 'City zero-waste plans set diversion targets integrating organic composting, '
                      'textile collection, and construction debris recovery. Progress monitoring '
                      'publishes open dashboards holding departments accountable when landfills '
                      'expand despite rhetorical commitments. The writer expects circular economy '
                      'to mainstream when policy, finance, and design education reinforce each '
                      'other consistently. Training industrial designers in materials science '
                      'prevents incompatible polymer blends impossible to recycle economically. '
                      'Circular systems succeed when they reduce absolute material throughput, not '
                      'merely recycle growing volumes of single-use packaging. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes. Policymakers '
                      'increasingly demand reproducible evidence, open data, and independent '
                      'evaluation before scaling interventions beyond controlled pilot settings.'},
  'tfng': [{'question': 'Product-as-a-service retains manufacturer ownership of equipment.',
            'answer': 'True'},
           {'question': 'All companies freely publish repair schematics globally.',
            'answer': 'False'},
           {'question': 'Every city has achieved zero waste according to the passage.',
            'answer': 'Not Given'},
           {'question': 'Basel Convention relates to transboundary e-waste movement.',
            'answer': 'True'},
           {'question': "Behavioural nudges alone fully replace price signals in the author's "
                        'view.',
            'answer': 'False'}],
  'ynng': [{'question': 'The author wants enforcement beyond voluntary corporate pledges.',
            'answer': 'Yes'},
           {'question': 'The writer believes symbiosis replicates without facilitation support.',
            'answer': 'No'},
           {'question': 'The author supports ethical standards for secondary materials.',
            'answer': 'Yes'},
           {'question': 'The writer thinks recycling growing single-use volume equals true '
                        'circularity.',
            'answer': 'No'},
           {'question': 'The author links accounting standards to unlocking circular capital.',
            'answer': 'Yes'}],
  'matching_headings': [{'paragraph': 'B', 'correct': 'ii. Repair design and digital passports'},
                        {'paragraph': 'C', 'correct': 'iii. Industrial symbiosis facilitation'},
                        {'paragraph': 'D', 'correct': 'iv. Consumer culture and deposit schemes'},
                        {'paragraph': 'E', 'correct': 'v. E-waste trade and urban mining'},
                        {'paragraph': 'F',
                         'correct': 'vi. Green finance and lifecycle accounting'}],
  'headings_pool': ['i. Baroque feather hat monopolies',
                    'j. Repair design and digital passports',
                    'k. Industrial symbiosis facilitation',
                    'l. Consumer culture and deposit schemes',
                    'm. E-waste trade and urban mining',
                    'n. Green finance and lifecycle accounting',
                    'o. Ancient siege engine timber'],
  'matching_info': [{'question': 'discussion of right-to-repair conflicting with aftermarket '
                                 'revenue',
                     'paragraph': 'B'},
                    {'question': 'reference to regional facilitators brokering symbiosis',
                     'paragraph': 'C'},
                    {'question': 'mention of repair cafes and tool libraries', 'paragraph': 'D'},
                    {'question': 'examples of Basel Convention e-waste rules', 'paragraph': 'E'},
                    {'question': 'a conclusion about reducing absolute material throughput',
                     'paragraph': 'G'}],
  'sentence_completion': [{'question': 'Extended producer responsibility fees fund ____ '
                                       'infrastructure.',
                           'answer': 'collection'},
                          {'question': 'Digital passports document material ____ for sorters.',
                           'answer': 'composition'},
                          {'question': 'Deposit-return schemes use reverse ____ machines.',
                           'answer': 'vending'},
                          {'question': 'Urban mining recovers metals from material ____.',
                           'answer': 'stockpiles'}],
  'summary_completion': [{'question': 'Linear patterns generate landfill ____ from decomposing '
                                      'waste.',
                          'answer': 'methane'},
                         {'question': 'Symbiosis parks exchange by-products like waste ____ or '
                                      'CO2.',
                          'answer': 'heat'},
                         {'question': 'Lifecycle assessments guide public ____ rules.',
                          'answer': 'procurement'},
                         {'question': 'Designers need training to avoid incompatible polymer ____.',
                          'answer': 'blends'}],
  'table_completion': [{'question': 'Business shift | Functional outcomes replace one-off ____',
                        'answer': 'sales'},
                       {'question': 'Trade risk | Informal recycling exposes workers to ____ '
                                    'fractions',
                        'answer': 'hazardous'},
                       {'question': 'City policy | Open dashboards track landfill ____',
                        'answer': 'expansion'}],
  'mcq': [{'question': 'Paragraph A measures circularity beyond',
           'options': ['only recycling rates',
                       'material circulation and lifetime extension',
                       'banning all manufacturing',
                       'feather hats'],
           'answer': 'material circulation and lifetime extension'},
          {'question': 'According to paragraph C, replication needs',
           'options': ['trust and facilitation networks',
                       'no transport analysis',
                       'disposable goods',
                       'Basel bans only'],
           'answer': 'trust and facilitation networks'},
          {'question': 'Paragraph D says nudges fail without',
           'options': ['price signals internalising externalities',
                       'repair cafes alone',
                       'symbiosis parks',
                       'green bonds'],
           'answer': 'price signals internalising externalities'},
          {'question': 'Paragraph F notes insurance may reward',
           'options': ['modular reusable building components',
                       'single-use packaging growth',
                       'informal e-waste',
                       'unpublished dashboards'],
           'answer': 'modular reusable building components'},
          {'question': 'The final paragraph warns against recycling growing',
           'options': ['absolute throughput reductions',
                       'volumes of single-use packaging',
                       'composting',
                       'digital passports'],
           'answer': 'volumes of single-use packaging'}],
  'short_answer': [{'question': 'What model charges customers for functional outcomes?',
                    'answer': 'product-as-a-service',
                    'word_limit': 1},
                   {'question': 'What Danish industrial symbiosis site is cited as inspiration?',
                    'answer': 'Kalundborg',
                    'word_limit': 1},
                   {'question': 'What convention governs hazardous e-waste shipments?',
                    'answer': 'Basel',
                    'word_limit': 1},
                   {'question': 'What bonds finance eligible circular investments?',
                    'answer': 'green',
                    'word_limit': 1}]},
 {'quiz_number': 24,
  'title': 'Urban heat island mitigation',
  'topic_category': 'Environment',
  'paragraphs': {'A': 'Urban heat islands elevate city temperatures relative to surrounding '
                      'countryside as asphalt, concrete, and sparse vegetation absorb and '
                      're-radiate solar energy. Nighttime minima rise especially, limiting relief '
                      'for residents lacking air conditioning during heatwaves intensified by '
                      'climate change. Vulnerable populations including elderly tenants in poorly '
                      'insulated apartments face elevated hospitalisation risks when cooling '
                      'centres remain distant. Planners quantify heat exposure using satellite '
                      'land surface temperatures, street-level sensors, and equity maps targeting '
                      'interventions toward burdened neighbourhoods. Mitigation complements '
                      'emissions reduction because local cooling saves lives even as global '
                      'warming continues. Cross-disciplinary collaboration, sustained funding, and '
                      'careful communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'B': 'Cool roofs reflect more sunlight through high-albedo coatings or '
                      'light-coloured membranes, lowering attic temperatures and air-conditioning '
                      'demand. Green roofs support soil and plants delaying runoff while '
                      'insulating upper floors, though structural load limits restrict adoption on '
                      'older buildings. Tree canopies shade sidewalks and transpire moisture, '
                      'producing evaporative cooling felt several degrees lower beneath mature '
                      'crowns. The author notes maintenance budgets must accompany plantings lest '
                      'saplings die during droughts wasting municipal investments. Species '
                      'selection should favour drought-tolerant natives requiring less irrigation '
                      'conflicting with water conservation goals. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes.',
                 'C': 'Cool pavements use reflective aggregates or permeable designs reducing '
                      'surface heat storage and re-emission overnight. Permeable surfaces also '
                      'mitigate flash flooding by infiltrating stormwater, delivering cobenefits '
                      'when maintenance crews clear clogging debris regularly. Transit agencies '
                      'plant shade at bus stops where passengers wait exposed, addressing dignity '
                      'alongside thermal comfort. Construction specifications increasingly include '
                      'solar reflectance index thresholds for public projects setting market '
                      'precedents. The writer argues procurement rules can scale materials faster '
                      'than voluntary homeowner programmes alone. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes. Policymakers '
                      'increasingly demand reproducible evidence, open data, and independent '
                      'evaluation before scaling interventions beyond controlled pilot settings.',
                 'D': 'Urban forestry campaigns engage residents in stewardship adopting street '
                      'trees, building social capital while expanding canopy cover. Property '
                      'owners sometimes resist trees fearing root damage or leaf litter, requiring '
                      'outreach explaining long-term energy savings. Municipal tree equity scores '
                      'reveal lower canopy in low-income districts historically redlined into '
                      'industrial corridors. Remediating disparities demands sustained funding not '
                      'one-time plantings before election cycles. The author contends '
                      'environmental justice must centre heat mitigation planning explicitly. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes. Policymakers increasingly demand reproducible evidence, '
                      'open data, and independent evaluation before scaling interventions beyond '
                      'controlled pilot settings.',
                 'E': 'Building retrofit programmes insulate attics and seal leaks complementing '
                      'passive cooling strategies reducing mechanical dependence. Renters lack '
                      'incentives to invest when landlords capture neither costs nor benefits, '
                      'necessitating minimum efficiency standards. Energy assistance subsidies '
                      'should prioritise efficient fans and shading before expanding '
                      'fossil-powered cooling capacity. Grid operators worry simultaneous '
                      'air-conditioning spikes during heat events cause rolling blackouts '
                      'undermining health protections. The writer supports demand response '
                      'incentives rewarding precooling buildings before peak pricing hours. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes. Policymakers increasingly demand reproducible evidence, '
                      'open data, and independent evaluation before scaling interventions beyond '
                      'controlled pilot settings.',
                 'F': 'Zoning reforms encourage mid-rise infill with courtyards increasing '
                      'ventilation corridors rather than canyon-like street walls trapping heat. '
                      'Surface parking lots converted to mixed-use development reduce expansive '
                      'asphalt deserts radiating warmth across downtown districts. Water features '
                      'and misters provide localized relief in plazas though they consume water '
                      'cautiously in arid municipalities. Nighttime radiative cooling materials '
                      'experimentally release heat to the sky, an emerging research frontier for '
                      'arid climates. The author cautions that aesthetic water installations '
                      'cannot substitute systemic material and canopy changes. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes.',
                 'G': 'Monitoring evaluates mortality reductions and energy savings attributing '
                      'outcomes to specific interventions using control neighbourhoods. Open data '
                      'portals invite researchers verifying claims and adjusting models for '
                      'humidity and wind interactions. The writer expects heat action plans to '
                      'integrate mitigation with early warning systems activating outreach before '
                      'extremes. Long-term success couples physical upgrades with social '
                      'programmes checking isolated seniors during alerts. Cooler equitable cities '
                      'emerge when technical solutions align with housing policy, labour '
                      'protections, and community leadership. Cross-disciplinary collaboration, '
                      'sustained funding, and careful communication with affected communities '
                      'remain central to credible long-term outcomes. Policymakers increasingly '
                      'demand reproducible evidence, open data, and independent evaluation before '
                      'scaling interventions beyond controlled pilot settings.'},
  'tfng': [{'question': 'Urban heat islands raise city temperatures above rural surroundings.',
            'answer': 'True'},
           {'question': 'Cool roofs always eliminate need for any trees.', 'answer': 'False'},
           {'question': 'Every municipality publishes tree equity scores.', 'answer': 'Not Given'},
           {'question': 'Permeable pavements can reduce flash flooding.', 'answer': 'True'},
           {'question': 'The passage says water misters alone solve systemic heat storage.',
            'answer': 'False'}],
  'ynng': [{'question': 'The author insists maintenance budgets must accompany tree plantings.',
            'answer': 'Yes'},
           {'question': "The writer believes renters' incentive problems need efficiency "
                        'standards.',
            'answer': 'Yes'},
           {'question': 'The author centres environmental justice in heat planning.',
            'answer': 'Yes'},
           {'question': 'The writer claims aesthetic fountains replace canopy and materials.',
            'answer': 'No'},
           {'question': 'The author links cooling with social checks on isolated seniors.',
            'answer': 'Yes'}],
  'matching_headings': [{'paragraph': 'B',
                         'correct': 'ii. Cool roofs, green roofs, and tree canopies'},
                        {'paragraph': 'C', 'correct': 'iii. Reflective and permeable pavements'},
                        {'paragraph': 'D', 'correct': 'iv. Community forestry and tree equity'},
                        {'paragraph': 'E', 'correct': 'v. Building retrofits and grid peaks'},
                        {'paragraph': 'F',
                         'correct': 'vi. Zoning, parking conversion, and water features'}],
  'headings_pool': ['i. Medieval wax seal monopolies',
                    'j. Cool roofs, green roofs, and tree canopies',
                    'k. Reflective and permeable pavements',
                    'l. Community forestry and tree equity',
                    'm. Building retrofits and grid peaks',
                    'n. Zoning, parking conversion, and water features',
                    'o. Ancient pottery wheel bearings'],
  'matching_info': [{'question': 'discussion of drought-tolerant native species selection',
                     'paragraph': 'B'},
                    {'question': 'reference to solar reflectance index in procurement',
                     'paragraph': 'C'},
                    {'question': 'mention of redlined districts with lower canopy',
                     'paragraph': 'D'},
                    {'question': 'examples of demand response precooling before peaks',
                     'paragraph': 'E'},
                    {'question': 'a conclusion coupling upgrades with social programmes',
                     'paragraph': 'G'}],
  'sentence_completion': [{'question': 'Heat islands elevate especially nighttime ____.',
                           'answer': 'minima'},
                          {'question': 'Green roofs delay stormwater ____ while insulating floors.',
                           'answer': 'runoff'},
                          {'question': 'Transit agencies add shade at bus ____.',
                           'answer': 'stops'},
                          {'question': 'Radiative cooling materials release heat toward the ____.',
                           'answer': 'sky'}],
  'summary_completion': [{'question': 'Satellite data help map land surface ____.',
                          'answer': 'temperatures'},
                         {'question': 'Cool pavements lower surface heat ____ overnight.',
                          'answer': 'storage'},
                         {'question': 'Landlords may ignore retrofits without minimum efficiency '
                                      '____.',
                          'answer': 'standards'},
                         {'question': 'Parking lot conversion reduces asphalt ____ radiating '
                                      'warmth.',
                          'answer': 'deserts'}],
  'table_completion': [{'question': 'Health risk | Heatwaves raise hospitalisations among ____ '
                                    'tenants',
                        'answer': 'elderly'},
                       {'question': 'Grid issue | Simultaneous AC may cause rolling ____',
                        'answer': 'blackouts'},
                       {'question': 'Evaluation | Control neighbourhoods help attribute ____ '
                                    'reductions',
                        'answer': 'mortality'}],
  'mcq': [{'question': 'Paragraph A targets interventions using',
           'options': ['equity maps of heat exposure',
                       'only wealthy districts',
                       'banning satellites',
                       'ending cooling centres'],
           'answer': 'equity maps of heat exposure'},
          {'question': 'According to paragraph B, green roofs are limited by',
           'options': ['structural load on older buildings',
                       'lack of any plants',
                       'prohibition on albedo',
                       'no maintenance needs'],
           'answer': 'structural load on older buildings'},
          {'question': 'Paragraph D says canopy disparities link to histories of',
           'options': ['redlining into industrial corridors',
                       'excessive cool roofs',
                       'radiative sky materials',
                       'mister bans'],
           'answer': 'redlining into industrial corridors'},
          {'question': 'Paragraph F warns water features cannot substitute',
           'options': ['systemic material and canopy changes',
                       'any zoning reform',
                       'bus stop shade',
                       'energy assistance'],
           'answer': 'systemic material and canopy changes'},
          {'question': 'The final paragraph integrates mitigation with',
           'options': ['early warning and senior outreach',
                       'only parking lots',
                       'fossil cooling expansion',
                       'ending open data'],
           'answer': 'early warning and senior outreach'}],
  'short_answer': [{'question': 'What surfaces increase albedo on buildings?',
                    'answer': 'cool roofs',
                    'word_limit': 2},
                   {'question': 'What process from trees cools air beneath canopies?',
                    'answer': 'transpiration',
                    'word_limit': 1},
                   {'question': 'What index thresholds appear in construction specifications?',
                    'answer': 'solar reflectance',
                    'word_limit': 2},
                   {'question': 'What scores reveal lower canopy in disadvantaged districts?',
                    'answer': 'tree equity',
                    'word_limit': 2}]},
 {'quiz_number': 25,
  'title': 'Wetland carbon storage',
  'topic_category': 'Environment',
  'paragraphs': {'A': 'Wetlands including marshes, swamps, and peatlands store substantial soil '
                      'carbon accumulated over centuries when waterlogged conditions slow '
                      'decomposition. Draining for agriculture or development oxidises organic '
                      'soils, releasing carbon dioxide and sometimes exposing fertile but unstable '
                      'substrates. Methane emissions complicate climate accounting because '
                      'anaerobic microbes produce greenhouse gases even in intact wetlands, '
                      'varying by salinity and vegetation. Restoration rewets degraded areas, '
                      're-establishing hydrology that halts ongoing losses and gradually rebuilds '
                      'carbon stocks. Policy markets increasingly recognise wetland credits, '
                      'though measurement uncertainty exceeds simpler forest biomass '
                      'methodologies. Cross-disciplinary collaboration, sustained funding, and '
                      'careful communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'B': 'Peatlands in boreal and tropical regions hold disproportionate global soil '
                      'carbon, motivating international conservation agreements. Palm oil '
                      'expansion historically drained tropical peat, causing fires smouldering for '
                      'months releasing hazardous smoke across regions. Fire suppression and canal '
                      'blocking raise water tables, reducing oxidation and catastrophic combustion '
                      'risks during droughts. The author insists restoration include community '
                      'fire management training rather than relying solely on engineering '
                      'structures. Without governance, rewetting may conflict with existing '
                      'smallholder plots established before tenure mapping completed. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes. Cross-disciplinary collaboration, sustained funding, '
                      'and careful communication with affected communities remain central to '
                      'credible long-term outcomes.',
                 'C': 'Coastal blue carbon in mangroves and seagrasses sequesters carbon in '
                      'biomass and sediments while protecting shorelines from erosion. Mangrove '
                      'planting campaigns must select appropriate species and tidal zones; '
                      'misplanted trees die wasting funds and credibility. Aquaculture pond '
                      'conversion back to mangroves requires removing embankments restoring '
                      'natural inundation rhythms. Fishers worry restored areas may restrict '
                      'access unless zoning allows sustainable harvesting compatible with '
                      'ecological recovery. The writer supports co-designed zoning balancing '
                      'livelihoods with carbon and coastal defence benefits. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes. Policymakers '
                      'increasingly demand reproducible evidence, open data, and independent '
                      'evaluation before scaling interventions beyond controlled pilot settings.',
                 'D': 'Hydrological monitoring uses wells and satellite radar detecting subtle '
                      'ground movement indicating water table changes. Greenhouse gas flux towers '
                      'measure carbon dioxide and methane exchanges, informing models predicting '
                      'net climate benefits. Methodological debates continue whether short-term '
                      'methane spikes after rewetting negate long-term carbon gains. Scientists '
                      'advocate multi-decade monitoring before issuing credits, conflicting with '
                      'investor desires for rapid returns. The author contends patience aligns '
                      'science with integrity rather than premature credit issuance. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes. Policymakers increasingly demand reproducible evidence, '
                      'open data, and independent evaluation before scaling interventions beyond '
                      'controlled pilot settings.',
                 'E': 'Legal designations such as Ramsar sites provide frameworks protecting '
                      'wetlands of international importance from incompatible land use. Domestic '
                      'laws vary in enforcing prohibitions on drainage; corruption may permit '
                      'illegal peat extraction despite nominal protections. Land trusts and '
                      'indigenous territories secure management rights, combining traditional '
                      'burning calendars with modern remote sensing. Payment schemes must '
                      'compensate opportunity costs fairly or risk community opposition sabotaging '
                      'projects subtly. The writer believes tenure security underpins durable '
                      'carbon storage more than one-off planting events. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'F': 'Infrastructure projects like roads bisecting wetlands alter hydrology '
                      'thousands of metres beyond visible culverts unless designed with '
                      'eco-passages and water retention. Environmental impact assessments should '
                      'model hydrological connectivity, not only direct footprint areas. Climate '
                      'adaptation funding increasingly prioritises natural infrastructure '
                      'alternatives to grey seawalls where wetlands absorb surge energy. Engineers '
                      'collaborate with ecologists sizing restoration parcels delivering '
                      'measurable storm protection alongside carbon metrics. The author argues '
                      'multifunctional projects attract broader coalitions than carbon-only '
                      'narratives ignoring flood benefits. Cross-disciplinary collaboration, '
                      'sustained funding, and careful communication with affected communities '
                      'remain central to credible long-term outcomes. Policymakers increasingly '
                      'demand reproducible evidence, open data, and independent evaluation before '
                      'scaling interventions beyond controlled pilot settings.',
                 'G': 'Emerging remote sensing with lidar and hyperspectral imagery maps soil '
                      'organic carbon stocks across vast inaccessible mires. Machine learning '
                      'classifies degradation stages guiding prioritisation where limited budgets '
                      'cannot restore everything immediately. Open data initiatives share flux '
                      'measurements accelerating model refinement across research networks. The '
                      'writer expects wetland carbon finance to mature as methodologies harmonise '
                      'and governance strengthens globally. Protecting wet carbon ultimately '
                      'requires keeping water in place while respecting communities whose lives '
                      'intertwine with soggy landscapes. Cross-disciplinary collaboration, '
                      'sustained funding, and careful communication with affected communities '
                      'remain central to credible long-term outcomes. Policymakers increasingly '
                      'demand reproducible evidence, open data, and independent evaluation before '
                      'scaling interventions beyond controlled pilot settings.'},
  'tfng': [{'question': 'Waterlogged soils slow decomposition storing carbon.', 'answer': 'True'},
           {'question': 'Methane never emits from intact wetlands.', 'answer': 'False'},
           {'question': 'All palm plantations have been removed from peat globally.',
            'answer': 'Not Given'},
           {'question': 'Mangrove misplanting in wrong tidal zones can fail.', 'answer': 'True'},
           {'question': 'The passage says short monitoring periods suffice for all credits.',
            'answer': 'False'}],
  'ynng': [{'question': 'The author wants community fire training beyond engineering alone.',
            'answer': 'Yes'},
           {'question': 'The writer believes carbon-only narratives beat multifunctional projects.',
            'answer': 'No'},
           {'question': 'The author urges patience before premature credit issuance.',
            'answer': 'Yes'},
           {'question': 'The writer dismisses tenure security as irrelevant.', 'answer': 'No'},
           {'question': 'The author supports co-designed zoning with fishers.', 'answer': 'Yes'}],
  'matching_headings': [{'paragraph': 'B',
                         'correct': 'ii. Peat fires, canal blocking, and governance'},
                        {'paragraph': 'C',
                         'correct': 'iii. Mangrove restoration and fisher access'},
                        {'paragraph': 'D', 'correct': 'iv. Flux towers and methane debates'},
                        {'paragraph': 'E', 'correct': 'v. Ramsar sites, tenure, and payments'},
                        {'paragraph': 'F',
                         'correct': 'vi. Infrastructure hydrology and natural defence'}],
  'headings_pool': ['i. Baroque silverware assay marks',
                    'j. Peat fires, canal blocking, and governance',
                    'k. Mangrove restoration and fisher access',
                    'l. Flux towers and methane debates',
                    'm. Ramsar sites, tenure, and payments',
                    'n. Infrastructure hydrology and natural defence',
                    'o. Ancient loom shuttle weights'],
  'matching_info': [{'question': 'reference to smouldering peat fires during droughts',
                     'paragraph': 'B'},
                    {'question': 'discussion of aquaculture pond conversion to mangroves',
                     'paragraph': 'C'},
                    {'question': 'mention of greenhouse gas flux towers', 'paragraph': 'D'},
                    {'question': 'examples of land trusts with traditional burning calendars',
                     'paragraph': 'E'},
                    {'question': 'a conclusion about keeping water in place with communities',
                     'paragraph': 'G'}],
  'sentence_completion': [{'question': 'Draining wetlands oxidises organic soils releasing carbon '
                                       '____.',
                           'answer': 'dioxide'},
                          {'question': 'Canal blocking raises water ____ reducing fire risk.',
                           'answer': 'tables'},
                          {'question': 'Radar detects ground movement reflecting hydrological '
                                       '____.',
                           'answer': 'changes'},
                          {'question': 'Lidar helps map soil organic carbon ____',
                           'answer': 'stocks'}],
  'summary_completion': [{'question': 'Blue carbon includes mangroves and ____.',
                          'answer': 'seagrasses'},
                         {'question': 'Investors often want rapid returns conflicting with ____ '
                                      'monitoring.',
                          'answer': 'multi-decade'},
                         {'question': 'Roads may alter hydrology far beyond visible ____.',
                          'answer': 'culverts'},
                         {'question': 'Hyperspectral imagery classifies degradation ____ for '
                                      'prioritisation.',
                          'answer': 'stages'}],
  'table_completion': [{'question': 'Climate trade-off | Methane flux complicates net ____ '
                                    'accounting',
                        'answer': 'climate'},
                       {'question': 'Legal tool | Ramsar designation protects wetlands of '
                                    'international ____',
                        'answer': 'importance'},
                       {'question': 'Adaptation | Wetlands may replace grey ____ absorbing surge',
                        'answer': 'seawalls'}],
  'mcq': [{'question': 'Paragraph A notes wetland credits face',
           'options': ['less uncertainty than forests',
                       'more measurement uncertainty than simple forest biomass',
                       'no methane concerns',
                       'ban on restoration'],
           'answer': 'more measurement uncertainty than simple forest biomass'},
          {'question': 'According to paragraph B, restoration should include',
           'options': ['only canal engineering',
                       'community fire management training',
                       'palm expansion',
                       'ending governance'],
           'answer': 'community fire management training'},
          {'question': 'Paragraph C warns planting must respect',
           'options': ['appropriate tidal zones',
                       'only seagrass bans',
                       'aquaculture expansion',
                       'no fisher input'],
           'answer': 'appropriate tidal zones'},
          {'question': 'Paragraph D debates methane spikes after',
           'options': ['rewetting versus long-term carbon gains',
                       'road culverts only',
                       'Ramsar repeal',
                       'lidar bans'],
           'answer': 'rewetting versus long-term carbon gains'},
          {'question': 'The final paragraph says protection requires',
           'options': ['keeping water in place with communities',
                       'draining all peat',
                       'ignoring flux towers',
                       'ending blue carbon'],
           'answer': 'keeping water in place with communities'}],
  'short_answer': [{'question': 'What gas emits from anaerobic wetland microbes?',
                    'answer': 'methane',
                    'word_limit': 1},
                   {'question': 'What international designation protects key wetlands?',
                    'answer': 'Ramsar',
                    'word_limit': 1},
                   {'question': 'What coastal ecosystems store blue carbon?',
                    'answer': 'mangroves',
                    'word_limit': 1},
                   {'question': 'What sensing technology maps carbon stocks across mires?',
                    'answer': 'lidar',
                    'word_limit': 1}]},
 {'quiz_number': 26,
  'title': 'Direct air carbon capture',
  'topic_category': 'Environment',
  'paragraphs': {'A': 'Direct air carbon capture removes carbon dioxide from ambient air using '
                      'chemical sorbents or membranes, producing concentrated streams for '
                      'geological storage or utilisation. Unlike point-source scrubbers on power '
                      'plants, these systems address dispersed historical emissions but require '
                      'substantial energy per tonne captured. Investors fund pilot plants in '
                      'geothermal regions or paired with renewable electricity to limit lifecycle '
                      'emissions undermining climate benefits. Cost estimates remain high compared '
                      'with many mitigation alternatives, prompting debate about prioritisation in '
                      'constrained public budgets. Proponents argue niche deployment complements '
                      'rapid decarbonisation rather than delaying emissions cuts elsewhere. '
                      'Cross-disciplinary collaboration, sustained funding, and careful '
                      'communication with affected communities remain central to credible '
                      'long-term outcomes.',
                 'B': 'Solid amine sorbents and liquid hydroxide solutions cycle through '
                      'adsorption and regeneration driven by heat releasing pure CO2 streams. '
                      'Engineering challenges include sorbent degradation from moisture and '
                      'oxygen, necessitating frequent replacement increasing operating expenses. '
                      'Modular contactors maximise air flow contact while minimising pressure '
                      'drops consuming fan electricity. Learning curves may reduce costs as '
                      'manufacturing scales, echoing solar panel experience if sustained '
                      'investment continues. The author cautions against extrapolating hopeful '
                      'trends without transparent pilot performance data. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes. Policymakers '
                      'increasingly demand reproducible evidence, open data, and independent '
                      'evaluation before scaling interventions beyond controlled pilot settings.',
                 'C': 'Geological storage injects captured CO2 into basalt formations or depleted '
                      'gas reservoirs trapped by caprock geology monitored for leakage. Monitoring '
                      'uses seismic surveys and tracers verifying plume behaviour decades after '
                      'injection ceases. Community consent processes address fears of induced '
                      'seismicity or groundwater contamination near injection wells. Indigenous '
                      'land rights demand consultation before siting pipelines crossing '
                      'territories en route to storage basins. The writer believes social licence '
                      'is as critical as technical containment assurance. Cross-disciplinary '
                      'collaboration, sustained funding, and careful communication with affected '
                      'communities remain central to credible long-term outcomes. Policymakers '
                      'increasingly demand reproducible evidence, open data, and independent '
                      'evaluation before scaling interventions beyond controlled pilot settings.',
                 'D': 'Utilisation pathways convert CO2 into synthetic fuels, aggregates, or '
                      'chemicals, temporarily recycling carbon unless paired with permanent '
                      'geological disposal. Marketing low-carbon concrete incorporating '
                      'mineralised CO2 highlights durable sequestration in building materials. '
                      'Critics note synthetic fuels re-release CO2 when combusted unless '
                      'atmospheric capture runs continuously balancing cycles. Lifecycle analyses '
                      'must account for energy sources powering conversion processes to avoid '
                      'vanity projects. The author supports utilisation only when monitoring '
                      'proves net long-term removal. Cross-disciplinary collaboration, sustained '
                      'funding, and careful communication with affected communities remain central '
                      'to credible long-term outcomes. Policymakers increasingly demand '
                      'reproducible evidence, open data, and independent evaluation before scaling '
                      'interventions beyond controlled pilot settings.',
                 'E': 'Policy incentives include tax credits per tonne stored and public '
                      'procurement preferring materials with verified embedded carbon removal. '
                      'Carbon market integrity frameworks guard against double counting between '
                      'corporate claims and national inventories. Environmental justice advocates '
                      'question whether large installations benefit neighbouring communities or '
                      'merely export visual industrialisation. Job training programmes for '
                      'maintenance technicians can align local workforce development with facility '
                      'operations. The writer contends benefit-sharing agreements should accompany '
                      'siting in disadvantaged regions. Cross-disciplinary collaboration, '
                      'sustained funding, and careful communication with affected communities '
                      'remain central to credible long-term outcomes. Policymakers increasingly '
                      'demand reproducible evidence, open data, and independent evaluation before '
                      'scaling interventions beyond controlled pilot settings.',
                 'F': 'Energy integration pairs capture with waste heat from industrial plants or '
                      'dedicated renewable parks powering regeneration cycles. Grid planners '
                      'analyse whether direct air capture loads justify transmission upgrades in '
                      'remote renewable-rich zones. Seasonal storage of captured CO2 as chilled '
                      'liquid may buffer utilisation plants operating intermittently. Hydrological '
                      'impacts from cooling needs must be assessed in arid landscapes hosting '
                      'solar arrays. The author urges holistic siting reviews crossing energy, '
                      'water, and land use boundaries. Cross-disciplinary collaboration, sustained '
                      'funding, and careful communication with affected communities remain central '
                      'to credible long-term outcomes. Policymakers increasingly demand '
                      'reproducible evidence, open data, and independent evaluation before scaling '
                      'interventions beyond controlled pilot settings.',
                 'G': 'International collaboration shares safety standards for transport and '
                      'injection preventing fragmented regulatory races to the bottom. Research '
                      'continues on passive capture materials reducing energy intensity, though '
                      'commercial readiness remains uncertain for decades possibly. The writer '
                      'expects direct air capture to occupy a specific niche in portfolios '
                      'achieving net negative emissions after deep decarbonisation. Transparency '
                      'about costs and energy use will determine public acceptance better than '
                      'slogans promising easy techno-fixes. Responsible deployment stores carbon '
                      'durably while accelerating the transition away from fossil fuels still '
                      'dominating emissions today. Cross-disciplinary collaboration, sustained '
                      'funding, and careful communication with affected communities remain central '
                      'to credible long-term outcomes.'},
  'tfng': [{'question': 'Direct air capture targets ambient rather than only flue gas.',
            'answer': 'True'},
           {'question': 'Captured carbon utilisation always guarantees permanent removal without '
                        'geology.',
            'answer': 'False'},
           {'question': 'Every pilot pairs with geothermal or renewable energy.',
            'answer': 'Not Given'},
           {'question': 'Sorbent degradation from moisture raises operating costs.',
            'answer': 'True'},
           {'question': 'The passage presents direct air capture as replacing all other '
                        'mitigation.',
            'answer': 'False'}],
  'ynng': [{'question': 'The author demands transparent pilot data before cost extrapolation.',
            'answer': 'Yes'},
           {'question': 'The writer believes social licence is less important than geology.',
            'answer': 'No'},
           {'question': 'The author supports utilisation only with proven net long-term removal.',
            'answer': 'Yes'},
           {'question': 'The writer endorses easy techno-fix slogans over transparency.',
            'answer': 'No'},
           {'question': 'The author positions capture as niche after deep decarbonisation.',
            'answer': 'Yes'}],
  'matching_headings': [{'paragraph': 'B',
                         'correct': 'ii. Sorbent cycles and engineering challenges'},
                        {'paragraph': 'C',
                         'correct': 'iii. Geological storage and community consent'},
                        {'paragraph': 'D',
                         'correct': 'iv. Utilisation pathways and lifecycle limits'},
                        {'paragraph': 'E', 'correct': 'v. Incentives, integrity, and justice'},
                        {'paragraph': 'F', 'correct': 'vi. Energy integration and siting reviews'}],
  'headings_pool': ['i. Medieval guild pewter standards',
                    'j. Sorbent cycles and engineering challenges',
                    'k. Geological storage and community consent',
                    'l. Utilisation pathways and lifecycle limits',
                    'm. Incentives, integrity, and justice',
                    'n. Energy integration and siting reviews',
                    'o. Ancient bridge anchor stones'],
  'matching_info': [{'question': 'description of adsorption and heat regeneration cycles',
                     'paragraph': 'B'},
                    {'question': 'reference to seismic monitoring of CO2 plumes', 'paragraph': 'C'},
                    {'question': 'discussion of synthetic fuels re-releasing CO2 when combusted',
                     'paragraph': 'D'},
                    {'question': 'mention of tax credits per tonne stored', 'paragraph': 'E'},
                    {'question': 'a conclusion pairing durable storage with fossil transition',
                     'paragraph': 'G'}],
  'sentence_completion': [{'question': 'Capture systems need substantial energy per tonne ____.',
                           'answer': 'captured'},
                          {'question': 'Basalt formations may trap CO2 beneath caprock ____.',
                           'answer': 'geology'},
                          {'question': 'Mineralised CO2 in concrete offers durable ____.',
                           'answer': 'sequestration'},
                          {'question': 'Passive capture materials aim to cut energy ____.',
                           'answer': 'intensity'}],
  'summary_completion': [{'question': 'Modular contactors balance airflow with fan electricity '
                                      '____.',
                          'answer': 'consumption'},
                         {'question': 'Indigenous consultation should precede pipeline ____ across '
                                      'territories.',
                          'answer': 'crossings'},
                         {'question': 'Integrity frameworks prevent double ____ in carbon markets.',
                          'answer': 'counting'},
                         {'question': 'Seasonal storage may buffer intermittent utilisation ____.',
                          'answer': 'plants'}],
  'table_completion': [{'question': 'Cost debate | Capture remains expensive versus many ____ '
                                    'alternatives',
                        'answer': 'mitigation'},
                       {'question': 'Justice | Facilities should include benefit-sharing in '
                                    'disadvantaged ____',
                        'answer': 'regions'},
                       {'question': 'Policy goal | Net negative emissions follow deep ____',
                        'answer': 'decarbonisation'}],
  'mcq': [{'question': 'Paragraph A contrasts direct air capture with',
           'options': ['only forest planting',
                       'point-source flue scrubbers',
                       'banning renewables',
                       'geothermal bans'],
           'answer': 'point-source flue scrubbers'},
          {'question': 'According to paragraph B, costs may fall with',
           'options': ['manufacturing scale and learning curves',
                       'hiding pilot data',
                       'moisture ignoring',
                       'ending sorbents'],
           'answer': 'manufacturing scale and learning curves'},
          {'question': 'Paragraph D warns synthetic fuels may',
           'options': ['re-release CO2 when combusted',
                       'guarantee permanent removal alone',
                       'ban lifecycle analysis',
                       'eliminate geology'],
           'answer': 're-release CO2 when combusted'},
          {'question': 'Paragraph E mentions integrity frameworks preventing',
           'options': ['double counting', 'all tax credits', 'job training', 'renewable pairing'],
           'answer': 'double counting'},
          {'question': 'The final paragraph urges responsible deployment while',
           'options': ['accelerating fossil transition away',
                       'delaying fossil phaseout',
                       'ending transparency',
                       'ignoring water impacts'],
           'answer': 'accelerating fossil transition away'}],
  'short_answer': [{'question': 'What chemical class includes solid capture materials?',
                    'answer': 'amines',
                    'word_limit': 1},
                   {'question': 'What rock type is named for geological storage?',
                    'answer': 'basalt',
                    'word_limit': 1},
                   {'question': 'What surveys monitor stored CO2 plumes?',
                    'answer': 'seismic',
                    'word_limit': 1},
                   {'question': 'What credits incentivise each tonne stored?',
                    'answer': 'tax',
                    'word_limit': 1}]}]
