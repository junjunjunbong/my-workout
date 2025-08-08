// Mock AI routine generation - in a real app, this would call an actual AI service
export const generateAIRoutine = async (userData) => {
  try {
    // In a real implementation, this would call an AI API
    // For now, we'll simulate AI-generated routines based on user data
    
    // Extract user preferences and workout history
    const { goal, experience, availableEquipment, workoutFrequency, workoutHistory } = userData;
    
    // Generate a routine based on user data
    let routine = {
      name: `${goal}을 위한 맞춤 루틴`,
      memo: `AI가 생성한 ${experience} 레벨을 위한 루틴입니다.`,
      items: []
    };
    
    // Sample routine generation logic based on user data
    if (goal === '근력 향상') {
      if (experience === '초보자') {
        routine.items = [
          { exercise: '스쿼트', category: '하체', sets: 3, reps: '8-12' },
          { exercise: '덤벨프레스', category: '상체', sets: 3, reps: '8-12' },
          { exercise: '랫풀다운', category: '상체', sets: 3, reps: '8-12' },
          { exercise: '루마니안 데드리프트', category: '하체', sets: 3, reps: '8-12' }
        ];
      } else if (experience === '중급자') {
        routine.items = [
          { exercise: '데드리프트', category: '전신', sets: 4, reps: '6-10' },
          { exercise: '벤치프레스', category: '상체', sets: 4, reps: '6-10' },
          { exercise: '바벨로우', category: '상체', sets: 4, reps: '6-10' },
          { exercise: '스쿼트', category: '하체', sets: 4, reps: '6-10' }
        ];
      } else {
        routine.items = [
          { exercise: '클린&프레스', category: '전신', sets: 5, reps: '3-8' },
          { exercise: '오버헤드프레스', category: '상체', sets: 5, reps: '3-8' },
          { exercise: '풀업', category: '상체', sets: 5, reps: '3-8' },
          { exercise: '프론트 스쿼트', category: '하체', sets: 5, reps: '3-8' }
        ];
      }
    } else if (goal === '체중 감량') {
      routine.items = [
        { exercise: '버피', category: '전신', sets: 3, reps: '10-15' },
        { exercise: '런닝', category: '유산소', sets: 1, reps: '30분' },
        { exercise: '마운틴클라이머', category: '전신', sets: 3, reps: '30초' },
        { exercise: '플랭크', category: '전신', sets: 3, reps: '30-60초' }
      ];
    } else { // For muscle building
      if (experience === '초보자') {
        routine.items = [
          { exercise: '덤벨프레스', category: '상체', sets: 3, reps: '10-15' },
          { exercise: '레그프레스', category: '하체', sets: 3, reps: '10-15' },
          { exercise: '덤벨로우', category: '상체', sets: 3, reps: '10-15' },
          { exercise: '레그컬', category: '하체', sets: 3, reps: '10-15' }
        ];
      } else if (experience === '중급자') {
        routine.items = [
          { exercise: '벤치프레스', category: '상체', sets: 4, reps: '8-12' },
          { exercise: '스쿼트', category: '하체', sets: 4, reps: '8-12' },
          { exercise: '바벨로우', category: '상체', sets: 4, reps: '8-12' },
          { exercise: '루마니안 데드리프트', category: '하체', sets: 4, reps: '8-12' }
        ];
      } else {
        routine.items = [
          { exercise: '데드리프트', category: '전신', sets: 5, reps: '6-10' },
          { exercise: '오버헤드프레스', category: '상체', sets: 5, reps: '6-10' },
          { exercise: '인클라인 덤벨프레스', category: '상체', sets: 5, reps: '6-10' },
          { exercise: '불가리안 스플릿 스쿼트', category: '하체', sets: 5, reps: '6-10' }
        ];
      }
    }
    
    // Filter exercises based on available equipment
    if (!availableEquipment.includes('덤벨')) {
      routine.items = routine.items.filter(item => item.exercise !== '덤벨프레스' && item.exercise !== '덤벨로우' && item.exercise !== '덤벨숄더프레스' && item.exercise !== '덤벨컬');
    }
    
    if (!availableEquipment.includes('바벨')) {
      routine.items = routine.items.filter(item => item.exercise !== '벤치프레스' && item.exercise !== '스쿼트' && item.exercise !== '데드리프트' && item.exercise !== '바벨로우' && item.exercise !== '오버헤드프레스' && item.exercise !== '바벨컬');
    }
    
    return routine;
  } catch (error) {
    throw new Error('AI 루틴 생성에 실패했습니다.');
  }
};