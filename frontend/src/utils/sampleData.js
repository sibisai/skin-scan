export const sampleImages = {
  skin_disease: [
    { id: 'eczema_1', label: 'Eczema', path: '/samples/skin_disease/eczema_1.jpg' },
    { id: 'eczema_2', label: 'Eczema', path: '/samples/skin_disease/eczema_2.jpg' },
    { id: 'fungal_1', label: 'Fungal', path: '/samples/skin_disease/fungal_1.jpg' },
    { id: 'fungal_2', label: 'Fungal', path: '/samples/skin_disease/fungal_2.jpg' },
    { id: 'acne_1', label: 'Acne', path: '/samples/skin_disease/acne_1.jpg' },
    { id: 'acne_2', label: 'Acne', path: '/samples/skin_disease/acne_2.jpg' },
    { id: 'psoriasis_1', label: 'Psoriasis', path: '/samples/skin_disease/psoriasis_1.jpg' },
    { id: 'psoriasis_2', label: 'Psoriasis', path: '/samples/skin_disease/psoriasis_2.jpg' },
    { id: 'scabies_1', label: 'Scabies', path: '/samples/skin_disease/scabies_1.jpg' },
    { id: 'scabies_2', label: 'Scabies', path: '/samples/skin_disease/scabies_2.jpg' },
    { id: 'healthy_1', label: 'Healthy', path: '/samples/skin_disease/healthy_1.jpg' },
    { id: 'healthy_2', label: 'Healthy', path: '/samples/skin_disease/healthy_2.jpg' },
  ],
};

export const modelInfo = {
  skin_disease: {
    name: 'Skin Condition Analysis',
    description: 'Identifies common skin conditions from phone camera photos.',
    accuracy: '85%',
    classes: ['Acne', 'Eczema', 'Fungal', 'Healthy', 'Psoriasis', 'Scabies'],
    imageType: 'Skin Photo',
  },
};

export const conditionDescriptions = {
  'eczema': 'Inflammatory skin condition causing red, itchy patches.',
  'fungal': 'Fungal infection appearing as circular, scaly patches.',
  'acne': 'Skin condition with pimples and inflamed bumps.',
  'psoriasis': 'Autoimmune condition causing thick, scaly patches.',
  'scabies': 'Parasitic infestation causing intense itching.',
  'healthy': 'Normal skin without visible conditions.',
};
