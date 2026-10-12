export const formatCurrency = (amount: number | string | undefined | null): string => {
  if (amount === undefined || amount === null) return '₹ 0.00';
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;
  if (isNaN(num)) return '₹ 0.00';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2,
    minimumFractionDigits: 2,
  }).format(num);
};

export const formatCarat = (carat: number | string | undefined | null): string => {
  if (carat === undefined || carat === null) return '0.000 ct';
  const num = typeof carat === 'string' ? parseFloat(carat) : carat;
  if (isNaN(num)) return '0.000 ct';
  return `${num.toFixed(3)} ct`;
};

export const formatWeightGrams = (grams: number | string | undefined | null): string => {
  if (grams === undefined || grams === null) return '0.000 g';
  const num = typeof grams === 'string' ? parseFloat(grams) : grams;
  if (isNaN(num)) return '0.000 g';
  return `${num.toFixed(3)} g`;
};

export const formatDate = (dateStr: string | undefined | null): string => {
  if (!dateStr) return '-';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  } catch {
    return dateStr;
  }
};
